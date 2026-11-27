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
      <p>Siteline collects public legislative and meeting records from local governments, structures them, and provides them through this website, feeds and an API.</p>
      <h2>Your account</h2>
      <p>You are responsible for activity under your account, API keys and private feed links. Keep them secret; revoke or delete any that may have leaked.</p>
      <h2>Permitted use</h2>
      <ul>
        <li>Free and Pro: use within your own organisation, including in analysis and reports for your clients.</li>
        <li>Team: additionally share the data across your organisation's internal systems.</li>
        <li>Publishing or reselling the dataset, or a substantial part of it, needs our written agreement.</li>
        <li>Do not circumvent plan limits or share credentials between organisations.</li>
      </ul>
      <h2>Payment</h2>
      <p>Paid plans are billed monthly in advance through Stripe and renew until cancelled. You can cancel at any time; access continues to the end of the paid period.</p>
      <h2>Accuracy</h2>
      <p>Records come from third-party government systems and may be incomplete, late or wrong. Classifications, sizes and outcomes are derived automatically and can be mistaken. The linked official record is authoritative. Nothing here is legal, investment or land-use advice.</p>
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
      <p>Public government records about land use, policy and infrastructure. Records can include the names of officials, staff and applicants exactly as they appear in the official public record; Siteline does not add to or profile them.</p>
      <h2>What we hold about you</h2>
      <ul>
        <li>Your email address and a salted hash of your password.</li>
        <li>Hashes of session tokens and API keys, never the keys themselves.</li>
        <li>Your saved watches and their feed links.</li>
        <li>A daily count of API requests per account.</li>
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
