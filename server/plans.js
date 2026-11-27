// Access tiers. "contributor" is not bought: an athlete earns it by sharing a
// deal of their own, which is how the dataset grows.
export const TIERS = {
  free: {
    name: 'Visitor', price: 0, explorer: false, rangefinder: false, comps: 0, export: false, dailyRequests: 50,
  },
  contributor: {
    name: 'Contributor', price: 0, explorer: true, rangefinder: true, comps: 8, export: false, dailyRequests: 200,
    tagline: 'For athletes. Share one deal, see them all.',
    features: ['Full benchmark explorer', 'Range finder for your next deal', '8 comparable deals per search', '12 months of access per deal shared'],
  },
  pro: {
    name: 'Pro', price: 299, explorer: true, rangefinder: true, comps: 50, export: true, dailyRequests: 5000,
    tagline: 'For agents, brands and collectives.',
    features: ['Everything, without contributing', '50 comparable deals per search', 'Printable fair-value comp reports', 'CSV export and API access', '5,000 API requests / day'],
  },
  team: {
    name: 'Team', price: 1499, explorer: true, rangefinder: true, comps: 200, export: true, dailyRequests: 50000,
    tagline: 'For athletic departments and agencies.',
    features: ['Everything in Pro', '200 comparable deals per search', '50,000 API requests / day', 'Internal redistribution licence', 'Priority support'],
  },
};

export const CONTRIBUTOR_DAYS = 365;

/** @param user  row with { plan }  @param contributing  has a live, non-rejected submission */
export function tierOf(user, contributing) {
  if (user?.plan === 'pro' || user?.plan === 'team') return user.plan;
  return user && contributing ? 'contributor' : 'free';
}
