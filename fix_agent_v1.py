from pathlib import Path
import re

router_path = Path("src/axion/commands/router.py")
identity_path = Path("src/axion/core/identity.py")
pyproject_path = Path("pyproject.toml")

router = router_path.read_text(encoding="utf-8")

# 1. Initialize PlanStore safely
if "self.plan_store.initialize()" not in router:
    router = router.replace(
        """        self.agent_manager = agent_manager or AgentManager(
            self.plan_store,
            PlannerAgent(self.ai_core),
            self.task_store,
        )
""",
        """        self.agent_manager = agent_manager or AgentManager(
            self.plan_store,
            PlannerAgent(self.ai_core),
            self.task_store,
        )
        self.plan_store.initialize()
""",
    )

# 2. Add missing Agent Mode command handlers
agent_methods = r'''
    def _agent_command(self, argument: str) -> CommandResponse:
        """Handle /agent commands."""
        action, _, value = argument.partition(" ")
        action = action.lower().strip()
        value = value.strip()

        if action == "status":
            active_count = self.plan_store.count_plans("active")
            done_count = self.plan_store.count_plans("done")
            paused_count = self.plan_store.count_plans("paused")
            return CommandResponse(
                "\n".join(
                    [
                        "Agent Mode: enabled",
                        f"Active plans: {active_count}",
                        f"Paused plans: {paused_count}",
                        f"Done plans: {done_count}",
                    ]
                )
            )

        if action == "plan":
            if not value:
                return CommandResponse("Usage: /agent plan <goal>")

            result = self.agent_manager.create_plan(value, self.current_model)
            if result.success:
                log_activity("agent plan created", f"id={result.plan_id}")
                if result.fallback_used:
                    log_activity("planner fallback used", f"id={result.plan_id}")

            return CommandResponse(result.message)

        return CommandResponse("Usage: /agent status or /agent plan <goal>")

    def _plans_command(self, argument: str) -> CommandResponse:
        """Handle /plans commands."""
        status = argument.lower().strip() or None

        if status not in {None, *PLAN_STATUSES}:
            return CommandResponse("Usage: /plans, /plans active, /plans paused, or /plans done")

        plans = self.plan_store.list_plans(status)
        if not plans:
            if status:
                return CommandResponse(f"No {status} plans.")
            return CommandResponse("No agent plans saved yet.")

        return CommandResponse(self.agent_manager.format_plan_list(plans))

    def _plan_command(self, argument: str) -> CommandResponse:
        """Handle /plan commands."""
        action, _, value = argument.partition(" ")
        action = action.lower().strip()
        value = value.strip()

        if action == "show":
            plan_id = self._parse_plan_id(value)
            if plan_id is None:
                return CommandResponse("Usage: /plan show <id>")

            plan = self.plan_store.get_plan(plan_id)
            if plan is None:
                return CommandResponse(f"Plan {plan_id} was not found.")

            steps = self.plan_store.list_steps(plan_id)
            return CommandResponse(self.agent_manager.format_plan(plan, steps))

        if action == "next":
            plan_id = self._parse_plan_id(value)
            if plan_id is None:
                return CommandResponse("Usage: /plan next <id>")

            result = self.agent_manager.next_step(plan_id)
            return CommandResponse(result.message)

        if action == "done":
            parts = value.split()
            if len(parts) != 2:
                return CommandResponse("Usage: /plan done <id> <step_number>")

            plan_id = self._parse_plan_id(parts[0])
            step_number = self._parse_plan_id(parts[1])
            if plan_id is None or step_number is None:
                return CommandResponse("Usage: /plan done <id> <step_number>")

            result = self.agent_manager.complete_step(plan_id, step_number)
            if result.success:
                log_activity("plan step completed", f"plan={plan_id}, step={step_number}")

            return CommandResponse(result.message)

        if action == "status":
            plan_id_text, _, status = value.partition(" ")
            plan_id = self._parse_plan_id(plan_id_text)
            status = status.lower().strip()

            if plan_id is None or status not in PLAN_STATUSES:
                return CommandResponse("Usage: /plan status <id> <active|paused|done>")

            result = self.agent_manager.set_plan_status(plan_id, status)
            if result.success:
                log_activity("plan status changed", f"plan={plan_id}, status={status}")

            return CommandResponse(result.message)

        if action == "tasks":
            plan_id = self._parse_plan_id(value)
            if plan_id is None:
                return CommandResponse("Usage: /plan tasks <id>")

            result = self.agent_manager.convert_open_steps_to_tasks(plan_id)
            if result.success:
                log_activity("plan converted to tasks", f"plan={plan_id}, count={result.count}")

            return CommandResponse(result.message)

        return CommandResponse(
            "Usage: /plan show <id>, /plan next <id>, /plan done <id> <step_number>, /plan status <id> <active|paused|done>, or /plan tasks <id>"
        )

    def _parse_plan_id(self, value: str) -> int | None:
        """Parse a positive plan id."""
        try:
            plan_id = int(value)
        except ValueError:
            return None

        if plan_id < 1:
            return None

        return plan_id

'''

if "def _agent_command" not in router:
    marker = "    def _split_in_folder"
    if marker not in router:
        raise RuntimeError("Could not find insertion point in router.py")
    router = router.replace(marker, agent_methods + "\n" + marker)

router_path.write_text(router, encoding="utf-8")

# 3. Update identity version
identity = identity_path.read_text(encoding="utf-8")
identity = re.sub(r'AXION_VERSION\s*=\s*"[0-9.]+"', 'AXION_VERSION = "1.0"', identity)
identity_path.write_text(identity, encoding="utf-8")

# 4. Update pyproject version
pyproject = pyproject_path.read_text(encoding="utf-8")
pyproject = re.sub(r'version\s*=\s*"[0-9.]+"', 'version = "1.0.0"', pyproject)
pyproject_path.write_text(pyproject, encoding="utf-8")

print("Axion v1.0 Agent Mode patch applied.")