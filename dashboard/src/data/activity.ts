import type { ActivityEvent } from "@/types/skill-tree";

export const activityEvents: ActivityEvent[] = [
  { id: "a1", title: "Business Discovery discovered 18 companies", detail: "6 matched the high-confidence opportunity profile.", time: "2 min", status: "completed", departmentId: "intelligence" },
  { id: "a2", title: "Website Auditor completed 6 audits", detail: "Three conversion-critical findings need review.", time: "8 min", status: "completed", departmentId: "intelligence" },
  { id: "a3", title: "Verified AI Radar found 2 verified stories", detail: "Sources cross-checked and ready for content review.", time: "14 min", status: "available", departmentId: "marketing" },
  { id: "a4", title: "Outreach Drafting is waiting for approval", detail: "12 personalized messages are staged.", time: "21 min", status: "waiting-for-approval", departmentId: "sales" },
  { id: "a5", title: "Demo Deployer deployed a preview", detail: "Preview environment is healthy and shareable.", time: "38 min", status: "completed", departmentId: "operations" },
];
