// Access tiers. Free shows the record with a delay; paying removes the delay
// and adds alerts, export and API volume.
export const TIERS = {
  free: {
    name: 'Free', price: 0, embargoDays: 30, pageSize: 25, upcoming: false, export: false, watches: 0, dailyRequests: 100,
    tagline: 'See what is covered.',
    features: ['National summary and trends', 'Records older than 30 days', 'Coverage list', '100 API requests / day'],
  },
  pro: {
    name: 'Pro', price: 399, embargoDays: 0, pageSize: 200, upcoming: true, export: true, watches: 10, dailyRequests: 5000,
    tagline: 'For developers, brokers and consultants.',
    features: ['Live records, no delay', 'Upcoming hearings calendar', '10 saved watches with private alert feeds', 'CSV export and API', '5,000 API requests / day'],
  },
  team: {
    name: 'Team', price: 750, embargoDays: 0, pageSize: 1000, upcoming: true, export: true, watches: 100, dailyRequests: 50000,
    tagline: 'For funds, utilities and law firms.',
    features: ['Everything in Pro', '100 saved watches', '50,000 API requests / day', 'Internal redistribution licence', 'Priority coverage requests'],
  },
};
export const tierOf = (user) => (TIERS[user?.plan] ? user.plan : 'free');
