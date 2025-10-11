
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

class Database {
  constructor() {
    this.db = null;
  }

  connect() {
    return new Promise((resolve, reject) => {
      const dbPath = '/data/database.sqlite';
      this.db = new sqlite3.Database(dbPath, (err) => {
        if (err) {
          console.error('Error connecting to database:', err.message);
          reject(err);
        } else {
          console.log('Connected to SQLite database');
          resolve();
        }
      });
    });
  }

  getDateMetadata() {
    return new Promise((resolve, reject) => {
      const query = `
        SELECT
          DATE(published_date) as date,
          COUNT(*) as total_count,
          SUM(CASE WHEN recommendation_score = 'Must Read' THEN 1 ELSE 0 END) as must_read_count,
          SUM(CASE WHEN recommendation_score = 'Should Read' THEN 1 ELSE 0 END) as should_read_count
        FROM papers
        GROUP BY DATE(published_date)
        ORDER BY date DESC
      `;

      this.db.all(query, [], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  getAllDatesMetadata() {
    return new Promise((resolve, reject) => {
      const query = `
        SELECT
          COUNT(*) as total_count,
          SUM(CASE WHEN recommendation_score = 'Must Read' THEN 1 ELSE 0 END) as must_read_count,
          SUM(CASE WHEN recommendation_score = 'Should Read' THEN 1 ELSE 0 END) as should_read_count
        FROM papers
      `;

      this.db.get(query, [], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row);
        }
      });
    });
  }

  getDateRange() {
    return new Promise((resolve, reject) => {
      const query = `
        SELECT
          MIN(DATE(published_date)) as earliest_date,
          MAX(DATE(published_date)) as latest_date
        FROM papers
      `;

      this.db.get(query, [], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row);
        }
      });
    });
  }

  // Get max h-index values for a given date filter
  getMaxHIndexValues(dateFilter) {
    return new Promise((resolve, reject) => {
      let query;
      let params = [];

      if (dateFilter === 'all') {
        query = `
          SELECT
            MAX(highest_h_index) as max_highest_h_index,
            CAST(CEIL(MAX(average_h_index)) AS INTEGER) as max_average_h_index
          FROM papers
        `;
      } else {
        query = `
          SELECT
            MAX(highest_h_index) as max_highest_h_index,
            CAST(CEIL(MAX(average_h_index)) AS INTEGER) as max_average_h_index
          FROM papers
          WHERE DATE(published_date) = ?
        `;
        params = [dateFilter];
      }

      this.db.get(query, params, (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve({
            maxHighestHIndex: row.max_highest_h_index || 0,
            maxAverageHIndex: row.max_average_h_index || 0
          });
        }
      });
    });
  }


  // Helper function: Build WHERE clause for filters
  _buildWhereClause(filters) {
    const conditions = [];
    const params = [];

    // Date filter
    if (filters.date && filters.date !== 'all') {
      conditions.push('DATE(published_date) = ?');
      params.push(filters.date);
    }

    // Scoring status filter
    if (filters.scoring && filters.scoring.length > 0) {
      const placeholders = filters.scoring.map(() => '?').join(',');
      conditions.push(`llm_score_status IN (${placeholders})`);
      params.push(...filters.scoring);
    }

    // Recommendation filter
    if (filters.recommendation && filters.recommendation.length > 0) {
      const placeholders = filters.recommendation.map(() => '?').join(',');
      conditions.push(`recommendation_score IN (${placeholders})`);
      params.push(...filters.recommendation);
    }

    // Impact filter
    if (filters.impact && filters.impact.length > 0) {
      const placeholders = filters.impact.map(() => '?').join(',');
      conditions.push(`impact_score IN (${placeholders})`);
      params.push(...filters.impact);
    }

    // Novelty filter
    if (filters.novelty && filters.novelty.length > 0) {
      const placeholders = filters.novelty.map(() => '?').join(',');
      conditions.push(`novelty_score IN (${placeholders})`);
      params.push(...filters.novelty);
    }

    // Relevance filter (interacts with topics filter)
    // Skip relevance filtering if topics is empty array (clear mode)
    if (filters.relevance && filters.relevance.length > 0 && filters.topics !== null) {
      const topicsToCheck = filters.topics && filters.topics.length > 0
        ? filters.topics
        : ['agentic_ai', 'proximal_policy_optimization', 'reinforcement_learning', 'reasoning_models', 'inference_time_scaling'];

      const topicFieldMap = {
        'agentic_ai': 'agentic_ai_relevance',
        'proximal_policy_optimization': 'proximal_policy_optimization_relevance',
        'reinforcement_learning': 'reinforcement_learning_relevance',
        'reasoning_models': 'reasoning_models_relevance',
        'inference_time_scaling': 'inference_time_scaling_relevance'
      };

      const relevanceConditions = [];
      topicsToCheck.forEach(topic => {
        const field = topicFieldMap[topic];
        const placeholders = filters.relevance.map(() => '?').join(',');
        relevanceConditions.push(`${field} IN (${placeholders})`);
      });

      if (relevanceConditions.length > 0) {
        conditions.push(`(${relevanceConditions.join(' OR ')})`);
        // Add params for each topic checked
        topicsToCheck.forEach(() => {
          params.push(...filters.relevance);
        });
      }
    }

    // H-index status filter
    if (filters.h_index_status && filters.h_index_status.length > 0) {
      const placeholders = filters.h_index_status.map(() => '?').join(',');
      conditions.push(`h_index_status IN (${placeholders})`);
      params.push(...filters.h_index_status);
    }

    // Highest h-index range filter
    if (filters.highest_h_index_range) {
      conditions.push('highest_h_index BETWEEN ? AND ?');
      params.push(filters.highest_h_index_range.min, filters.highest_h_index_range.max);
    }

    // Average h-index range filter
    if (filters.average_h_index_range) {
      conditions.push('average_h_index BETWEEN ? AND ?');
      params.push(filters.average_h_index_range.min, filters.average_h_index_range.max);
    }

    return {
      whereClause: conditions.length > 0 ? 'WHERE ' + conditions.join(' AND ') : '',
      params
    };
  }

  // Helper function: Build ORDER BY clause for sorting
  _buildOrderByClause(sortBy, sortOrder, selectedTopics) {
    const order = sortOrder.toUpperCase() === 'ASC' ? 'ASC' : 'DESC';

    switch(sortBy) {
      case 'recommendation':
        // For recommendation, DESC means best first, so we flip the order
        // Tie-breakers: Highest H-Index > Average H-Index > Topic Relevance
        const maxRelevanceScore = this._buildMaxRelevanceScore(selectedTopics);
        return `
          ORDER BY
            CASE recommendation_score
              WHEN 'Must Read' THEN 1
              WHEN 'Should Read' THEN 2
              WHEN 'Can Skip' THEN 3
              WHEN 'Ignore' THEN 4
              ELSE 5
            END ${order === 'DESC' ? 'ASC' : 'DESC'},
            highest_h_index DESC NULLS LAST,
            average_h_index DESC NULLS LAST,
            ${maxRelevanceScore} DESC
        `;

      case 'relevance':
        return this._buildRelevanceOrderBy(selectedTopics, order);

      case 'highest_h_index':
        return `ORDER BY highest_h_index ${order} NULLS LAST`;

      case 'average_h_index':
        return `ORDER BY average_h_index ${order} NULLS LAST`;

      case 'arxiv_id':
        return `ORDER BY id ${order}`;

      case 'title':
        return `ORDER BY LOWER(title) ${order}`;
    }
  }

  // Helper function: Build max relevance score calculation across selected topics
  _buildMaxRelevanceScore(selectedTopics) {
    const topicsToCheck = selectedTopics && selectedTopics.length > 0
      ? selectedTopics
      : ['agentic_ai', 'proximal_policy_optimization', 'reinforcement_learning', 'reasoning_models', 'inference_time_scaling'];

    const topicFieldMap = {
      'agentic_ai': 'agentic_ai_relevance',
      'proximal_policy_optimization': 'proximal_policy_optimization_relevance',
      'reinforcement_learning': 'reinforcement_learning_relevance',
      'reasoning_models': 'reasoning_models_relevance',
      'inference_time_scaling': 'inference_time_scaling_relevance'
    };

    const relevanceCases = topicsToCheck.map(topic => {
      const field = topicFieldMap[topic];
      return `
        CASE ${field}
          WHEN 'Highly Relevant' THEN 4
          WHEN 'Moderately Relevant' THEN 3
          WHEN 'Tangentially Relevant' THEN 2
          WHEN 'Not Relevant' THEN 1
          ELSE 0
        END
      `;
    });

    // SQLite doesn't have GREATEST, so use MAX() function
    return `MAX(${relevanceCases.join(',')})`;
  }

  // Helper function: Build relevance ORDER BY based on selected topics
  _buildRelevanceOrderBy(selectedTopics, order) {
    const topicsToCheck = selectedTopics && selectedTopics.length > 0
      ? selectedTopics
      : ['agentic_ai', 'proximal_policy_optimization', 'reinforcement_learning', 'reasoning_models', 'inference_time_scaling'];

    const topicFieldMap = {
      'agentic_ai': 'agentic_ai_relevance',
      'proximal_policy_optimization': 'proximal_policy_optimization_relevance',
      'reinforcement_learning': 'reinforcement_learning_relevance',
      'reasoning_models': 'reasoning_models_relevance',
      'inference_time_scaling': 'inference_time_scaling_relevance'
    };

    const fields = topicsToCheck.map(t => topicFieldMap[t]);

    // Build OR conditions for each relevance level
    const highlyRelevantCondition = fields.map(f => `${f} = 'Highly Relevant'`).join(' OR ');
    const moderatelyRelevantCondition = fields.map(f => `${f} = 'Moderately Relevant'`).join(' OR ');
    const tangentiallyRelevantCondition = fields.map(f => `${f} = 'Tangentially Relevant'`).join(' OR ');
    const notRelevantCondition = fields.map(f => `${f} = 'Not Relevant'`).join(' OR ');

    return `
      ORDER BY
        CASE
          WHEN (${highlyRelevantCondition}) THEN 4
          WHEN (${moderatelyRelevantCondition}) THEN 3
          WHEN (${tangentiallyRelevantCondition}) THEN 2
          WHEN (${notRelevantCondition}) THEN 1
          ELSE 0
        END ${order},
        CASE recommendation_score
          WHEN 'Must Read' THEN 1
          WHEN 'Should Read' THEN 2
          WHEN 'Can Skip' THEN 3
          WHEN 'Ignore' THEN 4
          ELSE 5
        END ASC,
        highest_h_index DESC NULLS LAST,
        average_h_index DESC NULLS LAST
    `;
  }

  // Get papers with advanced filtering, sorting, and pagination
  getPapersWithFilters(filters, sortOptions, pagination) {
    return new Promise((resolve, reject) => {
      const { whereClause, params: whereParams } = this._buildWhereClause(filters);
      const orderByClause = this._buildOrderByClause(
        sortOptions.sortBy,
        sortOptions.sortOrder,
        filters.topics
      );

      const query = `
        SELECT
          id, title, authors, categories, category_enhancement, abstract, published_date, arxiv_url, pdf_url,
          scraper_status, intro_status, embedding_status,
          agentic_ai_score, proximal_policy_optimization_score, reinforcement_learning_score,
          reasoning_models_score, inference_time_scaling_score,
          llm_validation_status, agentic_ai_relevance, proximal_policy_optimization_relevance,
          reinforcement_learning_relevance, reasoning_models_relevance, inference_time_scaling_relevance,
          agentic_ai_justification, proximal_policy_optimization_justification, reinforcement_learning_justification,
          reasoning_models_justification, inference_time_scaling_justification,
          llm_score_status, summary, novelty_score, novelty_justification,
          impact_score, impact_justification, recommendation_score, recommendation_justification,
          h_index_status, semantic_scholar_url, total_authors, authors_found,
          highest_h_index, average_h_index, notable_authors_count, author_h_indexes
        FROM papers
        ${whereClause}
        ${orderByClause}
        LIMIT ? OFFSET ?
      `;

      const queryParams = [...whereParams, pagination.limit, pagination.offset];

      this.db.all(query, queryParams, (err, rows) => {
        if (err) {
          reject(err);
        } else {
          const papers = rows.map(row => ({
            ...row,
            authors: JSON.parse(row.authors || '[]'),
            categories: JSON.parse(row.categories || '[]'),
            author_h_indexes: JSON.parse(row.author_h_indexes || '[]')
          }));
          resolve(papers);
        }
      });
    });
  }

  // Get count of filtered papers for pagination
  getFilteredCount(filters) {
    return new Promise((resolve, reject) => {
      const { whereClause, params } = this._buildWhereClause(filters);

      const query = `
        SELECT COUNT(*) as total
        FROM papers
        ${whereClause}
      `;

      this.db.get(query, params, (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row.total);
        }
      });
    });
  }

  getPaperById(arxivId) {
    return new Promise((resolve, reject) => {
      const query = `
        SELECT
          id, title, authors, categories, category_enhancement, abstract, published_date, arxiv_url, pdf_url,
          scraper_status, intro_status, embedding_status,
          agentic_ai_score, proximal_policy_optimization_score, reinforcement_learning_score,
          reasoning_models_score, inference_time_scaling_score,
          llm_validation_status, agentic_ai_relevance, proximal_policy_optimization_relevance,
          reinforcement_learning_relevance, reasoning_models_relevance, inference_time_scaling_relevance,
          agentic_ai_justification, proximal_policy_optimization_justification, reinforcement_learning_justification,
          reasoning_models_justification, inference_time_scaling_justification,
          llm_score_status, summary, novelty_score, novelty_justification,
          impact_score, impact_justification, recommendation_score, recommendation_justification,
          h_index_status, semantic_scholar_url, total_authors, authors_found,
          highest_h_index, average_h_index, notable_authors_count, author_h_indexes
        FROM papers
        WHERE id = ?
      `;

      this.db.get(query, [arxivId], (err, row) => {
        if (err) {
          reject(err);
        } else if (!row) {
          resolve(null);
        } else {
          const paper = {
            ...row,
            authors: JSON.parse(row.authors || '[]'),
            categories: JSON.parse(row.categories || '[]'),
            author_h_indexes: JSON.parse(row.author_h_indexes || '[]')
          };
          resolve(paper);
        }
      });
    });
  }

  close() {
    if (this.db) {
      this.db.close((err) => {
        if (err) {
          console.error('Error closing database:', err.message);
        } else {
          console.log('Database connection closed');
        }
      });
    }
  }
}

module.exports = new Database();