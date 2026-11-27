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
      <p>Rangefinder publishes benchmarks of name, image and likeness (NIL) deal values, built from deal terms that athletes share anonymously. It is independent and is not affiliated with the NCAA, the College Sports Commission, NIL Go or any school or conference.</p>
      <h2>Who can use it</h2>
      <p>You must be 18 or older to create an account or submit a deal.</p>
      <h2>Submitting a deal</h2>
      <ul>
        <li>Submit only deals you were personally party to, and only accurate information.</li>
        <li>You are responsible for checking that sharing the terms does not breach a confidentiality clause in your contract.</li>
        <li>Do not include names, schools or brand names anywhere in a submission.</li>
        <li>You grant us a licence to use the submission in aggregated and anonymised form. You can withdraw a submission from your account at any time; it is then deleted.</li>
        <li>We may hold, reject or remove submissions that look inaccurate.</li>
      </ul>
      <h2>Using the data</h2>
      <ul>
        <li>Contributor and Pro access is for your own use and your organisation's internal use, including reports for the athletes or clients you represent.</li>
        <li>Do not attempt to identify any athlete or deal, or combine the data with other sources to do so.</li>
        <li>Publishing or reselling the data outside your organisation needs our written agreement.</li>
      </ul>
      <h2>Payment</h2>
      <p>Paid plans are billed monthly in advance through Stripe and renew until cancelled. You can cancel at any time; access continues to the end of the paid period.</p>
      <h2>No advice, no guarantee</h2>
      <p>Figures are self-reported and may be wrong. They are market context only — not legal, financial or eligibility advice, and not a determination of fair market value or of whether any deal will be cleared.</p>
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
      <h2>What we deliberately do not collect</h2>
      <p>Your name, school, team, and the name of any brand or collective. There are no fields for them.</p>
      <h2>What we hold</h2>
      <ul>
        <li><b>Account:</b> your email address and a salted hash of your password. Hashes of session tokens and API keys, never the keys themselves.</li>
        <li><b>Deals you submit:</b> sport, competition level, class year, role, region, follower count, payer type, industry, deal type, deliverables, length, amounts, exclusivity, whether an agent was involved, NIL Go outcome and signing quarter. Each is linked to your account so you can withdraw it and so access can be granted.</li>
        <li><b>Usage:</b> a daily count of API requests per account.</li>
        <li><b>Billing:</b> Stripe customer and subscription identifiers. Card details go to Stripe and never reach our servers.</li>
      </ul>
      <h2>What other people can see</h2>
      <p>Only statistics over groups of at least five deals, and individual deals with the amount rounded, followers shown as a range, and no region, role, account or exact figures. Your email is never shown to anyone, including moderators reviewing a submission.</p>
      <h2>Cookies</h2>
      <p>One essential cookie keeps you signed in. There are no advertising or analytics cookies.</p>
      <h2>Sharing</h2>
      <p>We do not sell account data. It is shared only with processors needed to run the service (hosting, and Stripe for payments).</p>
      <h2>Your choices</h2>
      <p>Withdraw any deal from your account page; it is deleted immediately. Ask us to export or delete your account at any time: <Contact />.</p>
    </Page>
  );
}
