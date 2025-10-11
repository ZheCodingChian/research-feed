const express = require('express');
const db = require('../database/db');
const { validateAllParameters } = require('../validation/papersValidator');
const router = express.Router();

// GET /api/papers/details/:arxivId - Get single paper by arXiv ID
router.get('/details/:arxivId', async (req, res) => {
  try {
    const { arxivId } = req.params;

    const arxivIdRegex = /^\d{4}\.\d{5}$/;
    if (!arxivIdRegex.test(arxivId)) {
      return res.status(400).json({
        success: false,
        error: 'Invalid arXiv ID format. Expected format: YYMM.NNNNN (e.g., 2501.12345)'
      });
    }

    const paper = await db.getPaperById(arxivId);

    if (!paper) {
      return res.status(404).json({
        success: false,
        error: `Paper with ID ${arxivId} not found`
      });
    }

    res.json({
      success: true,
      data: paper
    });
  } catch (error) {
    console.error('Error fetching paper details:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch paper details',
      details: error.message
    });
  }
});

// Helper function: Map API values to DB values
function mapFilterValues(filterType, values) {
  const mappings = {
    scoring: {
      'not_relevant_enough': 'not_relevant_enough',
      'completed': 'completed'
    },
    recommendation: {
      'must_read': 'Must Read',
      'should_read': 'Should Read',
      'can_skip': 'Can Skip',
      'can_ignore': 'Ignore'
    },
    impact: {
      'transformative': 'Transformative',
      'substantial': 'Substantial',
      'moderate': 'Moderate',
      'negligible': 'Negligible'
    },
    novelty: {
      'groundbreaking': 'Groundbreaking',
      'significant': 'Significant',
      'incremental': 'Incremental',
      'minimal': 'Minimal'
    },
    relevance: {
      'highly': 'Highly Relevant',
      'moderately': 'Moderately Relevant',
      'tangentially': 'Tangentially Relevant',
      'not_relevant': 'Not Relevant'
    },
    h_index_status: {
      'found': 'completed',
      'not_found': ['not_fetched', 'failed']
    }
  };

  if (!mappings[filterType]) return values;

  return values.map(v => {
    const mapped = mappings[filterType][v];
    if (Array.isArray(mapped)) return mapped;
    return mapped || v;
  }).flat();
}

// Helper function: Null out unselected topic fields
function filterTopicFields(papers, topicsMode, topicsValues) {
  // If "all" or "clear", return all fields
  if (topicsMode === 'all' || topicsMode === 'clear') {
    return papers;
  }

  // CSV mode - null out unselected topics
  const allTopics = ['agentic_ai', 'proximal_policy_optimization', 'reinforcement_learning', 'reasoning_models', 'inference_time_scaling'];
  const unselectedTopics = allTopics.filter(t => !topicsValues.includes(t));

  return papers.map(paper => {
    const filteredPaper = { ...paper };

    unselectedTopics.forEach(topic => {
      filteredPaper[`${topic}_score`] = null;
      filteredPaper[`${topic}_relevance`] = null;
      filteredPaper[`${topic}_justification`] = null;
    });

    return filteredPaper;
  });
}

// GET /api/papers - Get all papers with advanced filtering, sorting, and pagination
router.get('/', async (req, res) => {
  try {
    // STRICT VALIDATION - All parameters required
    const validation = validateAllParameters(req.query);

    if (!validation.valid) {
      return res.status(400).json({
        success: false,
        error: validation.error,
        parameter: validation.parameter
      });
    }

    const params = validation.parsed;

    // Build filters object
    const filters = {};

    // Date filter
    filters.date = params.date;

    // Topics filter - handle "all", "clear", or CSV
    if (params.topics.mode === 'all') {
      // No topic filtering
      filters.topics = undefined;
    } else if (params.topics.mode === 'clear') {
      // Clear = user doesn't care about topics, skip relevance filtering
      filters.topics = null;
    } else {
      // CSV mode
      filters.topics = params.topics.value;
    }

    // Scoring filter
    if (params.scoring.mode === 'all') {
      filters.scoring = undefined;
    } else if (params.scoring.mode === 'clear') {
      filters.scoring = ['__IMPOSSIBLE_VALUE__'];
    } else {
      filters.scoring = mapFilterValues('scoring', params.scoring.value);
    }

    // Recommendation filter
    if (params.recommendation.mode === 'all') {
      filters.recommendation = undefined;
    } else if (params.recommendation.mode === 'clear') {
      filters.recommendation = ['__IMPOSSIBLE_VALUE__'];
    } else {
      filters.recommendation = mapFilterValues('recommendation', params.recommendation.value);
    }

    // Impact filter
    if (params.impact.mode === 'all') {
      filters.impact = undefined;
    } else if (params.impact.mode === 'clear') {
      filters.impact = ['__IMPOSSIBLE_VALUE__'];
    } else {
      filters.impact = mapFilterValues('impact', params.impact.value);
    }

    // Novelty filter
    if (params.novelty.mode === 'all') {
      filters.novelty = undefined;
    } else if (params.novelty.mode === 'clear') {
      filters.novelty = ['__IMPOSSIBLE_VALUE__'];
    } else {
      filters.novelty = mapFilterValues('novelty', params.novelty.value);
    }

    // Relevance filter
    if (params.relevance.mode === 'all') {
      filters.relevance = undefined;
    } else if (params.relevance.mode === 'clear') {
      filters.relevance = ['__IMPOSSIBLE_VALUE__'];
    } else {
      filters.relevance = mapFilterValues('relevance', params.relevance.value);
    }

    // H-index status filter
    if (params.h_index_status.mode === 'all') {
      filters.h_index_status = undefined;
    } else if (params.h_index_status.mode === 'clear') {
      filters.h_index_status = ['__IMPOSSIBLE_VALUE__'];
    } else {
      filters.h_index_status = mapFilterValues('h_index_status', params.h_index_status.value);
    }

    // Highest h-index range filter
    if (params.highest_h_index_range.mode === 'all') {
      filters.highest_h_index_range = undefined;
    } else {
      filters.highest_h_index_range = params.highest_h_index_range.value;
    }

    // Average h-index range filter
    if (params.average_h_index_range.mode === 'all') {
      filters.average_h_index_range = undefined;
    } else {
      filters.average_h_index_range = params.average_h_index_range.value;
    }

    // Execute queries in parallel
    const offset = (params.page - 1) * params.limit;
    const [papers, totalCount, totalPapers, dateRange, maxHIndexValues] = await Promise.all([
      db.getPapersWithFilters(filters, { sortBy: params.sortBy, sortOrder: params.sortOrder }, { limit: params.limit, offset }),
      db.getFilteredCount(filters),
      db.getFilteredCount({ date: filters.date }),
      db.getDateRange(),
      db.getMaxHIndexValues(filters.date)
    ]);

    // Apply topics filter to response (null out unselected topic fields)
    const filteredPapers = filterTopicFields(papers, params.topics.mode, params.topics.value);

    const totalPages = Math.ceil(totalCount / params.limit);

    // Determine start and end dates
    let startDate, endDate;
    if (filters.date === 'all') {
      startDate = dateRange.earliest_date;
      endDate = dateRange.latest_date;
    } else {
      startDate = filters.date;
      endDate = filters.date;
    }

    res.json({
      success: true,
      data: {
        papers: filteredPapers,
        pagination: {
          currentPage: params.page,
          totalPages,
          totalCount,
          limit: params.limit,
          hasNextPage: params.page < totalPages,
          hasPrevPage: params.page > 1
        },
        metadata: {
          startDate,
          endDate,
          totalPapers,
          maxHighestHIndex: maxHIndexValues.maxHighestHIndex,
          maxAverageHIndex: maxHIndexValues.maxAverageHIndex
        },
        appliedFilters: {
          date: filters.date,
          topics: params.topics.mode === 'all' ? 'all' : params.topics.mode === 'clear' ? 'clear' : params.topics.value,
          scoring: filters.scoring,
          recommendation: filters.recommendation,
          impact: filters.impact,
          novelty: filters.novelty,
          relevance: filters.relevance,
          h_index_status: filters.h_index_status,
          highest_h_index_range: filters.highest_h_index_range,
          average_h_index_range: filters.average_h_index_range
        },
        sorting: {
          sortBy: params.sortBy,
          sortOrder: params.sortOrder
        }
      }
    });
  } catch (error) {
    console.error('Error fetching papers:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch papers',
      details: error.message
    });
  }
});

// GET /api/papers/metadata - Get metadata for landing page
router.get('/metadata', async (req, res) => {
  try {
    const [allDatesMetadata, datesMetadata] = await Promise.all([
      db.getAllDatesMetadata(),
      db.getDateMetadata()
    ]);

    res.json({
      success: true,
      metadata: {
        all_dates: allDatesMetadata,
        dates: datesMetadata
      }
    });
  } catch (error) {
    console.error('Error fetching metadata:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch metadata'
    });
  }
});

module.exports = router;
