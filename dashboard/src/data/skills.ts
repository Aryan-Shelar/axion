import type { NodeStatus, Skill } from "@/types/skill-tree";

const catalog: Record<string, [string, string][]> = {
  intelligence: [
    ["Business Discovery", "Finds promising businesses that match your ideal customer profile."],
    ["Google Maps Finder", "Surfaces local businesses from map-based market signals."],
    ["Startup Finder", "Identifies emerging companies by sector, stage, and momentum."],
    ["Website Auditor", "Reviews websites for positioning, conversion, and technical gaps."],
    ["Competitor Research", "Builds concise competitive landscapes and differentiation briefs."],
    ["AI Opportunity Detector", "Maps high-value workflows where applied AI can create leverage."],
    ["Opportunity Scorer", "Ranks opportunities by value, urgency, confidence, and effort."],
  ],
  marketing: [
    ["Verified AI Radar", "Tracks credible AI developments and filters low-confidence noise."],
    ["Verified Content Studio", "Transforms verified research into channel-ready content."],
    ["Carousel Builder", "Structures sharp, visual narratives for social carousels."],
    ["Reel Builder", "Creates concise short-form video concepts, hooks, and scripts."],
    ["Content Scheduler", "Coordinates an approved publishing cadence across channels."],
    ["Analytics Reviewer", "Explains content performance and recommends the next experiments."],
  ],
  sales: [
    ["Contact Research", "Builds concise contact profiles with role and relevance context."],
    ["Outreach Drafting", "Creates personalized outreach grounded in verified prospect signals."],
    ["Follow-up Sequence", "Plans respectful, multi-step follow-ups around prospect intent."],
    ["Reply Classifier", "Routes incoming replies by intent, urgency, and next action."],
    ["Meeting Booker", "Coordinates qualified meeting requests and scheduling context."],
    ["CRM Updater", "Keeps pipeline records structured, current, and action-oriented."],
  ],
  deals: [
    ["Lead Qualification", "Evaluates fit, readiness, authority, need, and commercial potential."],
    ["Offer Designer", "Packages capabilities into outcome-focused offers for each buyer."],
    ["Pricing Assistant", "Models transparent pricing options against scope and value."],
    ["Discovery Call Planner", "Prepares focused questions and evidence for discovery calls."],
    ["Proposal Builder", "Assembles clear proposals with scope, outcomes, and next steps."],
    ["Closing Assistant", "Surfaces open concerns and supports a clean decision process."],
  ],
  operations: [
    ["Solution Architect", "Turns client requirements into secure, practical solution designs."],
    ["Website Builder", "Coordinates the delivery of conversion-focused web experiences."],
    ["Automation Builder", "Designs dependable workflows that reduce repetitive operations."],
    ["API Integrator", "Plans robust connections between approved systems and services."],
    ["Demo Deployer", "Packages and deploys client-ready solution previews."],
    ["Demo Quality Assurance", "Validates demo flows, content, resilience, and presentation."],
  ],
  customer: [
    ["Client Onboarding", "Guides clients from signed agreement to an aligned kickoff."],
    ["Support Agent", "Triages support needs and prepares clear, contextual responses."],
    ["Knowledge Assistant", "Makes approved client knowledge easy to find and apply."],
    ["Client Reporting", "Creates concise progress, value, and performance summaries."],
    ["Feedback Analysis", "Finds themes and next actions across structured client feedback."],
  ],
  "back-office": [
    ["Document Generator", "Produces consistent operational documents from approved inputs."],
    ["Invoice Assistant", "Prepares invoice details and flags missing commercial context."],
    ["Contract Drafting", "Creates review-ready contract drafts from standard terms."],
    ["Credential Manager", "Tracks secure credential configuration without exposing secrets."],
    ["Audit Logs", "Maintains a readable trail of important system and operator actions."],
    ["System Monitor", "Observes skill health, configuration, and operational anomalies."],
  ],
};

const statuses: NodeStatus[] = ["available", "completed", "available", "running", "waiting-for-approval", "not-configured", "failed"];
const slug = (value: string) => value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");

export const skills: Skill[] = Object.entries(catalog).flatMap(([departmentId, entries], departmentIndex) =>
  entries.map(([name, description], index) => ({
    id: slug(name),
    name,
    departmentId,
    description,
    status: statuses[(index + departmentIndex) % statuses.length],
    autonomy: index % 3 === 0 ? "Autonomous" : index % 3 === 1 ? "Supervised" : "Assisted",
    tools: index % 2 ? ["Browser", "Workspace"] : ["Research", "Structured data"],
    dependencies: index === 0 ? ["AXION Brain"] : [entries[Math.max(0, index - 1)][0]],
    outputs: [index % 2 ? "Action brief" : "Structured report", "Activity event"],
    lastRun: index % 4 === 0 ? "12 min ago" : index % 4 === 1 ? "Today, 14:32" : index % 4 === 2 ? "Yesterday" : "Never",
    metrics: [
      { label: "Success rate", value: `${91 + ((index + departmentIndex) % 8)}%` },
      { label: "Runs this week", value: String(8 + index * 3 + departmentIndex) },
      { label: "Avg. duration", value: `${1 + (index % 4)}m ${12 + departmentIndex * 4}s` },
    ],
  })),
);

export const skillById = Object.fromEntries(skills.map((skill) => [skill.id, skill]));
