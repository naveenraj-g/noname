import { ZSAError } from "zsa";
import { Endpoint, KnowledgeBase, Agent } from "./admin";

export interface IEndpointsProps {
  endpoints: Endpoint[] | null;
  error: ZSAError | null;
}

export type TEndpoint = Endpoint;

export interface IKnowledgeBaseProps {
  knowledgeBase: KnowledgeBase[] | null;
  error: ZSAError | null;
}

export type TKnowledgeBase = KnowledgeBase;

export interface IAgentsProps {
  agents: Agent[] | null;
  error: ZSAError | null;
}

export type TAgent = Agent;
