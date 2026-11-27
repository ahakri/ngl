// Starting-point legal pages. They describe how the product actually behaves;
// have counsel review and add your company's legal name and address before launch.
import { useSession } from '../hooks.js';

function Page({ title, children }) {
  return (
    <div className="docs" style={{ maxWidth: 760 }}>
      <h1>{title}</h1>
      <p style={{ marginTop: 8 }}>Last updated 27 November 2026.</p>
      {children}
    </div>
  );
}

function Contact() {
  const { config } = useSession();
  return config?.sales_email ? <a href={`mailto:${config.sales_email}`}>{config.sales_email}</a> : <>the contact address on this site</>;
}

export function Terms() {
  return (
    <Page title="Terms of Service">
      <h2>The service</h2>
      <p>Uptake provides statistics about adoption of software packages and machine-learning models, derived from public sources, through this website and an API.</p>
      <h2>Your account</h2>
      <p>You are responsible for activity under your account and API keys. Keep keys secret and revoke any that may have leaked.</p>
      <h2>Permitted use</h2>
      <ul>
        <li>Free and Pro: use the data inside your own organisation, including in internal analysis, models and reports.</li>
        <li>Team: additionally share the data with colleagues across your organisation's internal systems.</li>
        <li>Publishing or reselling the data, or a substantial part of it, outside your organisation needs our written agreement.</li>
        <li>Do not circumvent plan limits, share keys between organisations, or disrupt the service.</li>
      </ul>
      <h2>Payment</h2>
      <p>Paid plans are billed monthly in advance through Stripe and renew until cancelled. You can cancel at any time from your account; access continues to the end of the paid period.</p>
      <h2>The data</h2>
      <p>Figures are estimates derived from third-party public statistics, which can be revised, delayed or change methodology. Downloads include automated traffic and are not a count of people. The data is provided as is, without warranty, and is not investment advice.</p>
      <h2>Liability</h2>
      <p>To the extent the law allows, our total liability is limited to the fees you paid in the twelve months before the claim.</p>
      <h2>Changes and contact</h2>
      <p>We may update these terms and will post the new version here. Questions: <Contact />.</p>
    </Page>
  );
}

export function Privacy() {
  return (
    <Page title="Privacy Policy">
      <h2>What the dataset contains</h2>
      <p>Only aggregate, public statistics about software packages and models. It contains no personal data about developers or users of those packages.</p>
      <h2>What we hold about you</h2>
      <ul>
        <li>Your email address and a salted hash of your password.</li>
        <li>Hashes of your session tokens and API keys — never the keys themselves.</li>
        <li>A daily count of API requests per account, for quota enforcement.</li>
        <li>If you subscribe: Stripe customer and subscription identifiers. Card details go to Stripe and never reach our servers.</li>
      </ul>
      <h2>Cookies</h2>
      <p>One essential cookie keeps you signed in. There are no advertising or analytics cookies.</p>
      <h2>Sharing</h2>
      <p>We do not sell account data. It is shared only with processors needed to run the service (hosting, and Stripe for payments).</p>
      <h2>Your choices</h2>
      <p>Ask us to export or delete your account at any time: <Contact />.</p>
    </Page>
  );
}
