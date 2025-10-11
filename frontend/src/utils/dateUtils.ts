import { DateMetadata } from '../types/api';

/**
 * Formats an ISO date string to "Day, dd Month yyyy" format
 * @param dateString - ISO date string like "2024-09-21"
 * @returns Formatted string like "Saturday, 21 September 2024"
 */
export function formatDateForCard(dateString: string): string {
  const formatted = new Intl.DateTimeFormat('en-GB', {
    weekday: 'long',
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  }).format(new Date(dateString));

  // Add comma after weekday
  return formatted.replace(/^(\w+)/, '$1,');
}

/**
 * Formats an ISO date string to "dd Month yyyy" format (no weekday)
 * @param dateString - ISO date string like "2024-09-21"
 * @returns Formatted string like "21 September 2024"
 */
export function formatDateForAllTimeCard(dateString: string): string {
  return new Intl.DateTimeFormat('en-GB', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  }).format(new Date(dateString));
}

/**
 * Calculates date range from array of date metadata
 * @param dates - Array of DateMetadata objects
 * @returns Object with start and end date strings
 */
export function getDateRange(dates: DateMetadata[]): { start: string; end: string } {
  if (dates.length === 0) {
    return { start: '', end: '' };
  }

  const sortedDates = dates.map(d => d.date).sort();
  return {
    start: sortedDates[0],
    end: sortedDates[sortedDates.length - 1]
  };
}