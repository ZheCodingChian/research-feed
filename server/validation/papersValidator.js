// Strict validation for /api/papers endpoint
// All parameters are required, case-sensitive, no trimming, no defaults

const ALLOWED_VALUES = {
  sortBy: ['recommendation', 'relevance', 'highest_h_index', 'average_h_index', 'arxiv_id', 'title'],
  sortOrder: ['asc', 'desc'],
  topics: ['agentic_ai', 'proximal_policy_optimization', 'reinforcement_learning', 'reasoning_models', 'inference_time_scaling'],
  recommendation: ['must_read', 'should_read', 'can_skip', 'can_ignore'],
  impact: ['transformative', 'substantial', 'moderate', 'negligible'],
  novelty: ['groundbreaking', 'significant', 'incremental', 'minimal'],
  relevance: ['highly', 'moderately', 'tangentially', 'not_relevant'],
  scoring: ['completed', 'not_relevant_enough'],
  h_index_status: ['found', 'not_found']
};

// Required parameters
const REQUIRED_PARAMS = [
  'page',
  'limit',
  'sortBy',
  'sortOrder',
  'date',
  'topics',
  'recommendation',
  'impact',
  'novelty',
  'relevance',
  'scoring',
  'h_index_status',
  'highest_h_index_range',
  'average_h_index_range'
];

function validateRequired(queryParams) {
  const missing = [];

  for (const param of REQUIRED_PARAMS) {
    if (queryParams[param] === undefined) {
      missing.push(param);
    }
  }

  if (missing.length > 0) {
    return {
      valid: false,
      error: `Missing required parameter(s): ${missing.join(', ')}`,
      parameter: missing[0]
    };
  }

  return { valid: true };
}

function validatePage(page) {
  const parsed = parseInt(page);
  if (isNaN(parsed) || parsed < 1 || parsed.toString() !== page.toString()) {
    return {
      valid: false,
      error: 'page must be a positive integer',
      parameter: 'page'
    };
  }
  return { valid: true, value: parsed };
}

function validateLimit(limit) {
  const parsed = parseInt(limit);
  if (isNaN(parsed) || parsed < 1 || parsed > 100 || parsed.toString() !== limit.toString()) {
    return {
      valid: false,
      error: 'limit must be a positive integer between 1 and 100',
      parameter: 'limit'
    };
  }
  return { valid: true, value: parsed };
}

function validateSortBy(sortBy) {
  if (!ALLOWED_VALUES.sortBy.includes(sortBy)) {
    return {
      valid: false,
      error: `sortBy must be one of: ${ALLOWED_VALUES.sortBy.join(', ')}`,
      parameter: 'sortBy'
    };
  }
  return { valid: true, value: sortBy };
}

function validateSortOrder(sortOrder) {
  if (!ALLOWED_VALUES.sortOrder.includes(sortOrder)) {
    return {
      valid: false,
      error: 'sortOrder must be "asc" or "desc"',
      parameter: 'sortOrder'
    };
  }
  return { valid: true, value: sortOrder };
}

function validateDate(date) {
  if (date === 'all') {
    return { valid: true, value: 'all' };
  }

  const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
  if (!dateRegex.test(date)) {
    return {
      valid: false,
      error: 'date must be "all" or YYYY-MM-DD format',
      parameter: 'date'
    };
  }

  return { valid: true, value: date };
}

function validateCSVField(fieldName, value, allowedValues) {
  // Check for empty string
  if (value === '') {
    return {
      valid: false,
      error: `${fieldName} cannot be empty`,
      parameter: fieldName
    };
  }

  // Check for "all" or "clear"
  if (value === 'all') {
    return { valid: true, value: 'all', mode: 'all' };
  }

  if (value === 'clear') {
    return { valid: true, value: 'clear', mode: 'clear' };
  }

  // Must be CSV - split by comma (NO TRIMMING)
  const values = value.split(',');

  // Check if mixing "all"/"clear" with other values
  if (values.includes('all') || values.includes('clear')) {
    return {
      valid: false,
      error: `${fieldName} cannot mix "all" or "clear" with other values`,
      parameter: fieldName
    };
  }

  // Check for empty parts (e.g., "rlhf,,weak_supervision")
  if (values.some(v => v === '')) {
    return {
      valid: false,
      error: `${fieldName} contains empty values in CSV`,
      parameter: fieldName
    };
  }

  // Validate each value
  for (const v of values) {
    if (!allowedValues.includes(v)) {
      return {
        valid: false,
        error: `${fieldName} contains invalid value "${v}". Allowed: ${allowedValues.join(', ')}, "all", "clear"`,
        parameter: fieldName
      };
    }
  }

  return { valid: true, value: values, mode: 'csv' };
}

function validateHIndexRange(fieldName, value) {
  // Check for "all"
  if (value === 'all') {
    return { valid: true, mode: 'all' };
  }

  // Check for empty string
  if (value === '') {
    return {
      valid: false,
      error: `${fieldName} cannot be empty`,
      parameter: fieldName
    };
  }

  // Must be in "min-max" format
  const match = value.match(/^(\d+)-(\d+)$/);
  if (!match) {
    return {
      valid: false,
      error: `${fieldName} must be "all" or "min-max" format (e.g., "0-100")`,
      parameter: fieldName
    };
  }

  const min = parseInt(match[1]);
  const max = parseInt(match[2]);

  // Validate min <= max
  if (min > max) {
    return {
      valid: false,
      error: `${fieldName} min value cannot be greater than max value`,
      parameter: fieldName
    };
  }

  return {
    valid: true,
    mode: 'range',
    value: { min, max }
  };
}


function validateAllParameters(queryParams) {
  // 1. Check all required parameters are present
  const requiredCheck = validateRequired(queryParams);
  if (!requiredCheck.valid) return requiredCheck;

  // 2. Validate page
  const pageCheck = validatePage(queryParams.page);
  if (!pageCheck.valid) return pageCheck;

  // 3. Validate limit
  const limitCheck = validateLimit(queryParams.limit);
  if (!limitCheck.valid) return limitCheck;

  // 4. Validate sortBy
  const sortByCheck = validateSortBy(queryParams.sortBy);
  if (!sortByCheck.valid) return sortByCheck;

  // 5. Validate sortOrder
  const sortOrderCheck = validateSortOrder(queryParams.sortOrder);
  if (!sortOrderCheck.valid) return sortOrderCheck;

  // 6. Validate date
  const dateCheck = validateDate(queryParams.date);
  if (!dateCheck.valid) return dateCheck;

  // 7. Validate topics
  const topicsCheck = validateCSVField('topics', queryParams.topics, ALLOWED_VALUES.topics);
  if (!topicsCheck.valid) return topicsCheck;

  // 8. Validate recommendation
  const recommendationCheck = validateCSVField('recommendation', queryParams.recommendation, ALLOWED_VALUES.recommendation);
  if (!recommendationCheck.valid) return recommendationCheck;

  // 9. Validate impact
  const impactCheck = validateCSVField('impact', queryParams.impact, ALLOWED_VALUES.impact);
  if (!impactCheck.valid) return impactCheck;

  // 10. Validate novelty
  const noveltyCheck = validateCSVField('novelty', queryParams.novelty, ALLOWED_VALUES.novelty);
  if (!noveltyCheck.valid) return noveltyCheck;

  // 11. Validate relevance
  const relevanceCheck = validateCSVField('relevance', queryParams.relevance, ALLOWED_VALUES.relevance);
  if (!relevanceCheck.valid) return relevanceCheck;

  // 12. Validate scoring
  const scoringCheck = validateCSVField('scoring', queryParams.scoring, ALLOWED_VALUES.scoring);
  if (!scoringCheck.valid) return scoringCheck;

  // 13. Validate h_index_status
  const hIndexStatusCheck = validateCSVField('h_index_status', queryParams.h_index_status, ALLOWED_VALUES.h_index_status);
  if (!hIndexStatusCheck.valid) return hIndexStatusCheck;

  // 14. Validate highest_h_index_range
  const highestHIndexRangeCheck = validateHIndexRange('highest_h_index_range', queryParams.highest_h_index_range);
  if (!highestHIndexRangeCheck.valid) return highestHIndexRangeCheck;

  // 15. Validate average_h_index_range
  const averageHIndexRangeCheck = validateHIndexRange('average_h_index_range', queryParams.average_h_index_range);
  if (!averageHIndexRangeCheck.valid) return averageHIndexRangeCheck;

  // All valid - return parsed values
  return {
    valid: true,
    parsed: {
      page: pageCheck.value,
      limit: limitCheck.value,
      sortBy: sortByCheck.value,
      sortOrder: sortOrderCheck.value,
      date: dateCheck.value,
      topics: topicsCheck,
      recommendation: recommendationCheck,
      impact: impactCheck,
      novelty: noveltyCheck,
      relevance: relevanceCheck,
      scoring: scoringCheck,
      h_index_status: hIndexStatusCheck,
      highest_h_index_range: highestHIndexRangeCheck,
      average_h_index_range: averageHIndexRangeCheck
    }
  };
}

module.exports = {
  validateAllParameters,
  ALLOWED_VALUES
};
