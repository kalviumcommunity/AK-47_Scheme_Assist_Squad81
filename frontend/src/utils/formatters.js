/**
 * formatters.js - Utility formatters for SchemeAssist
 */

export function formatCurrency(amount) {
  if (amount === undefined || amount === null) return '₹0';
  if (typeof amount === 'string') return amount;
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount);
}

export function formatDate(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  if (isNaN(date.getTime())) return dateStr;
  return new Intl.DateTimeFormat('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  }).format(date);
}

export function formatAadhaar(aadhaarStr) {
  if (!aadhaarStr) return '•••• •••• ••••';
  const clean = aadhaarStr.replace(/\D/g, '');
  if (clean.length < 12) return aadhaarStr;
  return `•••• •••• ${clean.slice(-4)}`;
}

export function getMatchBadgeColor(matchPercentage) {
  if (matchPercentage >= 90) {
    return 'bg-gov-success-light text-gov-success border-gov-success/20';
  } else if (matchPercentage >= 70) {
    return 'bg-primary-50 text-primary border-primary/20';
  } else {
    return 'bg-gov-warning-light text-gov-warning border-gov-warning/20';
  }
}
