import type { Department } from "@/types/skill-tree";

export const departments: Department[] = [
  { id: "intelligence", name: "Intelligence", shortLabel: "INTEL", color: "#20D6FF", description: "Discover signals, markets, competitors, and high-value opportunities." },
  { id: "marketing", name: "Marketing", shortLabel: "MKTG", color: "#A78BFA", description: "Turn verified intelligence into coordinated content and campaigns." },
  { id: "sales", name: "Sales", shortLabel: "SALES", color: "#34D399", description: "Research, engage, and progress the right prospects." },
  { id: "deals", name: "Deals", shortLabel: "DEALS", color: "#FBBF24", description: "Shape opportunities into clear, compelling commercial outcomes." },
  { id: "operations", name: "Operations", shortLabel: "OPS", color: "#FB7185", description: "Design, build, integrate, and quality-check client solutions." },
  { id: "customer", name: "Customer", shortLabel: "CX", color: "#38BDF8", description: "Onboard, support, report, and learn from every client." },
  { id: "back-office", name: "Back Office", shortLabel: "ADMIN", color: "#F472B6", description: "Protect the operational core with reliable business administration." },
];

export const departmentById = Object.fromEntries(departments.map((department) => [department.id, department]));
