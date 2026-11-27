// Plans: what each tier can see and how much it can call.
export const PLANS = {
  free: {
    name: 'Free',
    price: 0,
    historyDays: 90,
    shareWeeks: 12,
    moversLimit: 5,
    modelsLimit: 25,
    dailyRequests: 100,
    export: false,
    tagline: 'Explore the leaderboards.',
    features: ['All 9 category leaderboards', '90 days of history', 'Top 5 movers per ecosystem', '100 API requests / day'],
  },
  pro: {
    name: 'Pro',
    price: 199,
    historyDays: 3650,
    shareWeeks: 104,
    moversLimit: 100,
    modelsLimit: 500,
    dailyRequests: 10000,
    export: true,
    tagline: 'For analysts, founders and GTM teams.',
    features: ['Full history, break-adjusted', 'Complete movers & breakout feed', 'CSV export of signals and series', '10,000 API requests / day', 'Hugging Face org & task share, top 500 models'],
  },
  team: {
    name: 'Team',
    price: 999,
    historyDays: 3650,
    shareWeeks: 104,
    moversLimit: 100,
    modelsLimit: 2500,
    dailyRequests: 100000,
    export: true,
    tagline: 'For funds and data teams.',
    features: ['Everything in Pro', '100,000 API requests / day', 'Full Hugging Face model panel', 'Internal redistribution licence', 'Priority support & custom watchlists'],
  },
};

export const planOf = (user) => PLANS[user?.plan] ? user.plan : 'free';
export const limitsOf = (user) => PLANS[planOf(user)];
