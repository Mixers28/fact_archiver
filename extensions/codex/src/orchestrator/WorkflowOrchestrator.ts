export interface WorkflowAgentDefinition {
  id: string;
  label: string;
  description?: string;
}

export interface WorkflowAgentResult {
  agentId: string;
  label: string;
  prompt: string;
  context?: string;
}

export type WorkflowAgentState = "pending" | "running" | "done" | "cancelled";

export interface WorkflowAgentStatus {
  agentId: string;
  label: string;
  state: WorkflowAgentState;
}

export interface RunWorkflowOptions {
  token?: { isCancellationRequested: boolean };
  onUpdate?: (statuses: WorkflowAgentStatus[]) => void;
}

interface WorkflowState {
  task: string;
  results: WorkflowAgentResult[];
  statuses: WorkflowAgentStatus[];
}

export class WorkflowOrchestrator {
  constructor(
    private readonly agents: WorkflowAgentDefinition[],
    private readonly getInstructions: (participantName: string) => Promise<string>
  ) {}

  async runWorkflow(task: string, options?: RunWorkflowOptions): Promise<WorkflowAgentResult[]> {
    const state: WorkflowState = {
      task,
      results: [],
      statuses: this.agents.map(agent => ({
        agentId: agent.id,
        label: agent.label,
        state: "pending" as WorkflowAgentState
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

  private buildAgentPrompt(input: { task: string; instructions?: string; context?: string }) {
    const lines: string[] = [];

    if (input.instructions) {
      lines.push(input.instructions.trim(), "");
    }

    lines.push("Task", input.task.trim());

    if (input.context) {
      lines.push("", "Context from earlier agents", input.context.trim());
    }

    lines.push(
      "",
      "Expectations",
      "- Summarize your intended deliverables",
      "- Call out risks or blockers quickly",
      "- Propose next actions or files to change if relevant",
      "",
      "Output format",
      "Summary:",
      "Decisions:",
      "Actions:",
      "Risks / dependencies:"
    );

    return lines.join("\n");
  }

  private buildContext(state: WorkflowState): string {
    if (state.results.length === 0) return "";

    const summarized = state.results.map(result => {
      const trimmed = this.truncate(result.prompt.replace(/\s+/g, " ").trim(), 180);
      return `- ${result.label}: ${trimmed}`;
    });

    return summarized.join("\n");
  }

  private truncate(text: string, maxLength: number): string {
    if (text.length <= maxLength) return text;
    return `${text.slice(0, maxLength - 3)}...`;
  }

  private setStatus(state: WorkflowState, agentId: string, agentState: WorkflowAgentState) {
    state.statuses = state.statuses.map(status =>
      status.agentId === agentId ? { ...status, state: agentState } : status
    );
  }

  private cancelRemaining(state: WorkflowState) {
    state.statuses = state.statuses.map(status => {
      if (status.state === "done") return status;
      return { ...status, state: "cancelled" };
    });
  }

  private emitStatus(state: WorkflowState, options?: RunWorkflowOptions) {
    if (!options?.onUpdate) return;
    options.onUpdate(state.statuses);
  }
}
