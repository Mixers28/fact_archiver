"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WorkflowOrchestrator = void 0;
class WorkflowOrchestrator {
    constructor(agents, getInstructions) {
        this.agents = agents;
        this.getInstructions = getInstructions;
    }
    async runWorkflow(task, options) {
        const state = {
            task,
            results: [],
            statuses: this.agents.map(agent => ({
                agentId: agent.id,
                label: agent.label,
                state: "pending"
            }))
        };
        this.emitStatus(state, options);
        for (const agent of this.agents) {
            if (options?.token?.isCancellationRequested) {
                this.cancelRemaining(state);
                this.emitStatus(state, options);
                break;
            }
            this.setStatus(state, agent.id, "running");
            this.emitStatus(state, options);
            const context = this.buildContext(state);
            const instructions = await this.getInstructions(agent.label);
            const prompt = this.buildAgentPrompt({
                task,
                instructions,
                context
            });
            state.results.push({
                agentId: agent.id,
                label: agent.label,
                prompt,
                context
            });
            this.setStatus(state, agent.id, "done");
            this.emitStatus(state, options);
        }
        return state.results;
    }
    buildAgentPrompt(input) {
        const lines = [];
        if (input.instructions) {
            lines.push(input.instructions.trim(), "");
        }
        lines.push("Task", input.task.trim());
        if (input.context) {
            lines.push("", "Context from earlier agents", input.context.trim());
        }
        lines.push("", "Expectations", "- Summarize your intended deliverables", "- Call out risks or blockers quickly", "- Propose next actions or files to change if relevant", "", "Output format", "Summary:", "Decisions:", "Actions:", "Risks / dependencies:");
        return lines.join("\n");
    }
    buildContext(state) {
        if (state.results.length === 0)
            return "";
        const summarized = state.results.map(result => {
            const trimmed = this.truncate(result.prompt.replace(/\s+/g, " ").trim(), 180);
            return `- ${result.label}: ${trimmed}`;
        });
        return summarized.join("\n");
    }
    truncate(text, maxLength) {
        if (text.length <= maxLength)
            return text;
        return `${text.slice(0, maxLength - 3)}...`;
    }
    setStatus(state, agentId, agentState) {
        state.statuses = state.statuses.map(status => status.agentId === agentId ? { ...status, state: agentState } : status);
    }
    cancelRemaining(state) {
        state.statuses = state.statuses.map(status => {
            if (status.state === "done")
                return status;
            return { ...status, state: "cancelled" };
        });
    }
    emitStatus(state, options) {
        if (!options?.onUpdate)
            return;
        options.onUpdate(state.statuses);
    }
}
exports.WorkflowOrchestrator = WorkflowOrchestrator;
//# sourceMappingURL=WorkflowOrchestrator.js.map