# Agent Chat UI

Agent Chat UI is a Next.js application which enables chatting with any LangGraph server with a `messages` key through a chat interface.

> [!NOTE]
> 🎥 Watch the video setup guide [here](https://youtu.be/lInrwVnZ83o).

## Setup

> [!TIP]
> Don't want to run the app locally? Use the deployed site here: [agentchat.vercel.app](https://agentchat.vercel.app)!

First, clone the repository, or run the [`npx` command](https://www.npmjs.com/package/create-agent-chat-app):

```bash
npx create-agent-chat-app
```

or

```bash
git clone https://github.com/langchain-ai/agent-chat-ui.git

cd agent-chat-ui
```

Install dependencies:

```bash
pnpm install
```

Run the app:

```bash
pnpm dev
```

The app will be available at `http://localhost:3000`.

## Usage

Once the app is running (or if using the deployed site), you'll be prompted to enter:

- **Deployment URL**: The URL of the LangGraph server you want to chat with. This can be a production or development URL.
- **Assistant/Graph ID**: The name of the graph, or ID of the assistant to use when fetching, and submitting runs via the chat interface.
- **LangSmith API Key**: (only required for connecting to deployed LangGraph servers) Your LangSmith API key to use when authenticating requests sent to LangGraph servers.

After entering these values, click `Continue`. You'll then be redirected to a chat interface where you can start chatting with your LangGraph server.

## Environment Variables

You can bypass the initial setup form by setting the following environment variables:

```bash
NEXT_PUBLIC_API_URL=http://localhost:2024
NEXT_PUBLIC_ASSISTANT_ID=agent
```

> [!TIP]
> If you want to connect to a production LangGraph server, read the [Going to Production](#going-to-production) section.

To use these variables:

1. Copy the `.env.example` file to a new file named `.env`
2. Fill in the values in the `.env` file
3. Restart the application

When these environment variables are set, the application will use them instead of showing the setup form.

## Hiding Messages in the Chat

You can control the visibility of messages within the Agent Chat UI in two main ways:

**1. Prevent Live Streaming:**

To stop messages from being displayed _as they stream_ from an LLM call, add the `langsmith:nostream` tag to the chat model's configuration. The UI normally uses `on_chat_model_stream` events to render streaming messages; this tag prevents those events from being emitted for the tagged model.

_Python Example:_

```python
from langchain_anthropic import ChatAnthropic

# Add tags via the .with_config method
model = ChatAnthropic().with_config(
    config={"tags": ["langsmith:nostream"]}
)
```

_TypeScript Example:_

```typescript
import { ChatAnthropic } from "@langchain/anthropic";

const model = new ChatAnthropic()
  // Add tags via the .withConfig method
  .withConfig({ tags: ["langsmith:nostream"] });
```

**Note:** Even if streaming is hidden this way, the message will still appear after the LLM call completes if it's saved to the graph's state without further modification.

**2. Hide Messages Permanently:**

To ensure a message is _never_ displayed in the chat UI (neither during streaming nor after being saved to state), prefix its `id` field with `do-not-render-` _before_ adding it to the graph's state, along with adding the `langsmith:do-not-render` tag to the chat model's configuration. The UI explicitly filters out any message whose `id` starts with this prefix.

_Python Example:_

```python
result = model.invoke([messages])
# Prefix the ID before saving to state
result.id = f"do-not-render-{result.id}"
return {"messages": [result]}
```

_TypeScript Example:_

```typescript
const result = await model.invoke([messages]);
// Prefix the ID before saving to state
result.id = `do-not-render-${result.id}`;
return { messages: [result] };
```

This approach guarantees the message remains completely hidden from the user interface.

## Rendering Artifacts

The Agent Chat UI supports rendering artifacts in the chat. Artifacts are rendered in a side panel to the right of the chat. To render an artifact, you can obtain the artifact context from the `thread.meta.artifact` field. Here's a sample utility hook for obtaining the artifact context:

```tsx
export function useArtifact<TContext = Record<string, unknown>>() {
  type Component = (props: {
    children: React.ReactNode;
    title?: React.ReactNode;
  }) => React.ReactNode;

  type Context = TContext | undefined;

  type Bag = {
    open: boolean;
    setOpen: (value: boolean | ((prev: boolean) => boolean)) => void;

    context: Context;
    setContext: (value: Context | ((prev: Context) => Context)) => void;
  };

  const thread = useStreamContext<
    { messages: Message[]; ui: UIMessage[] },
    { MetaType: { artifact: [Component, Bag] } }
  >();

  return thread.meta?.artifact;
}
```

After which you can render additional content using the `Artifact` component from the `useArtifact` hook:

```tsx
import { useArtifact } from "../utils/use-artifact";
import { LoaderIcon } from "lucide-react";

export function Writer(props: {
  title?: string;
  content?: string;
  description?: string;
}) {
  const [Artifact, { open, setOpen }] = useArtifact();

  return (
    <>
      <div
        onClick={() => setOpen(!open)}
        className="cursor-pointer rounded-lg border p-4"
      >
        <p className="font-medium">{props.title}</p>
        <p className="text-sm text-gray-500">{props.description}</p>
      </div>

      <Artifact title={props.title}>
        <p className="p-4 whitespace-pre-wrap">{props.content}</p>
      </Artifact>
    </>
  );
}
```

## 本地项目能力对照与接入规划

这一节用于记录当前 `agent-chat-ui` 在本仓库中的实际能力，以及未来参考
`langgraphjs/examples/ui-react` 接入更多 LangGraph 前端能力时的参考路径。

### 当前能力现状表（ASCII Matrix）

```text
+----------------------+----------+--------------------------------------+----------------------+
| 能力                 | 当前状态 | LangGraphJS example                  | 优先级               |
+----------------------+----------+--------------------------------------+----------------------+
| Tool Calls           | 已具备   | tool-calling-agent                   | 已有                 |
| Interrupt / HITL     | 已具备   | human-in-the-loop                    | 已有                 |
| Branch / Regenerate  | 已具备   | branching-chat                       | 已有                 |
| Artifact / UI 基础   | 已具备   | generative-ui related patterns       | 已有                 |
| Summary Messages     | 未实现   | summarization-agent                  | 第二优先级           |
| Reasoning Blocks     | 未实现   | reasoning-agent                      | 第二优先级           |
| Tool Progress        | 未实现   | tool-streaming                       | 第一优先级           |
| Reconnect Banner     | 未实现   | session-persistence                  | 第一优先级           |
| Custom Event Cards   | 未实现   | custom-streaming                     | 第四优先级           |
| Parallel Research    | 未实现   | parallel-research                    | 第四优先级           |
| Subagent Pipeline    | 未实现   | deepagent                            | 第三优先级           |
| Subagent + Tools     | 未实现   | deepagent-tools                      | 第三优先级           |
+----------------------+----------+--------------------------------------+----------------------+
```

### Example 参考表（ASCII Matrix）

```text
+----------------------+----------------------------------+----------------------+
| example              | 主要展示能力                     | 建议接入优先级       |
+----------------------+----------------------------------+----------------------+
| tool-calling-agent   | 基础 useStream + tool calls      | 已有                 |
| human-in-the-loop    | interrupt / approve / reject     | 已有                 |
| branching-chat       | branch / checkpoint / regenerate | 已有                 |
| session-persistence  | reconnectOnMount / thread 恢复   | 第一优先级           |
| tool-streaming       | tool progress                    | 第一优先级           |
| summarization-agent  | summary message                  | 第二优先级           |
| reasoning-agent      | reasoning blocks                 | 第二优先级           |
| deepagent            | subagent pipeline                | 第三优先级           |
| deepagent-tools      | subagent + tool calls            | 第三优先级           |
| parallel-research    | 多研究节点结果面板              | 第四优先级           |
| custom-streaming     | custom events cards              | 第四优先级           |
+----------------------+----------------------------------+----------------------+
```

### 当前项目已具备的能力

- **工具调用 Tool Calls**
  - 当前状态：已具备
  - 本地实现参考：`src/components/thread/messages/ai.tsx`
  - 说明：已支持渲染 tool calls 与 tool results。

- **人工审批 Interrupt / HITL**
  - 当前状态：已具备
  - 本地实现参考：`src/components/thread/agent-inbox/index.tsx`
  - 本地实现参考：`src/components/thread/agent-inbox/hooks/use-interrupted-actions.tsx`
  - 说明：已支持 interrupt 渲染、approve / edit / reject 提交。

- **分支切换 / Regenerate / 历史**
  - 当前状态：已具备
  - 本地实现参考：`src/components/thread/messages/ai.tsx`
  - 本地实现参考：`src/components/thread/messages/human.tsx`
  - 说明：已支持 branch 切换、编辑旧消息、regenerate。

- **Artifact / Generative UI 基础能力**
  - 当前状态：已具备
  - 本地实现参考：`src/components/thread/artifact.tsx`
  - 本地实现参考：`src/providers/Stream.tsx`
  - 说明：已支持 `uiMessageReducer` 路径和 artifact 面板渲染。

### 当前项目尚未具备的能力

- **摘要消息 Summary Messages**
  - 当前状态：未实现
  - 需要接入：摘要消息检测与专门 UI 卡片

- **推理区块 Reasoning Blocks**
  - 当前状态：未实现
  - 需要接入：reasoning content block 的识别与折叠展示

- **工具进度 Tool Progress**
  - 当前状态：未实现
  - 需要接入：工具执行中的流式进度卡片

- **自定义事件卡片 Custom Event Cards**
  - 当前状态：未实现
  - 需要接入：`progress` / `status` / `file-status` 自定义事件渲染

- **重连横幅 Reconnect Banner**
  - 当前状态：未实现
  - 需要接入：线程刷新后的恢复状态 UI

- **并行研究面板 Parallel Research Panel**
  - 当前状态：未实现
  - 需要接入：多研究节点的专门结果面板

- **子代理流水线 Subagent Pipeline**
  - 当前状态：未实现
  - 需要接入：deepagent / subagent 结果流式展示

- **带工具的子代理视图 Deep Agent with Tools**
  - 当前状态：未实现
  - 需要接入：subagent + tool call 联合展示

### LangGraphJS examples 能力矩阵

- **`tool-calling-agent`**
  - 展示能力：基础 `useStream` + tool calls
  - 前端参考：[tool-calling-agent/index.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/tool-calling-agent/index.tsx)
  - 后端参考：[tool-calling-agent/agent.ts](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/tool-calling-agent/agent.ts)

- **`human-in-the-loop`**
  - 展示能力：interrupt / approve / reject / edit / resume
  - 前端参考：[human-in-the-loop/index.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/human-in-the-loop/index.tsx)
  - 组件参考：[PendingApprovalCard.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/human-in-the-loop/components/PendingApprovalCard.tsx)
  - 后端参考：[human-in-the-loop/agent.ts](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/human-in-the-loop/agent.ts)

- **`summarization-agent`**
  - 展示能力：摘要中间件 / summary message
  - 前端参考：[summarization-agent/index.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/summarization-agent/index.tsx)
  - 后端参考：[summarization-agent/agent.ts](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/summarization-agent/agent.ts)

- **`reasoning-agent`**
  - 展示能力：推理内容单独流式展示
  - 前端参考：[reasoning-agent/index.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/reasoning-agent/index.tsx)
  - 后端参考：[reasoning-agent/agent.ts](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/reasoning-agent/agent.ts)

- **`tool-streaming`**
  - 展示能力：工具执行进度流
  - 前端参考：[tool-streaming/index.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/tool-streaming/index.tsx)
  - 组件参考：[ToolProgressCard.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/tool-streaming/components/ToolProgressCard.tsx)
  - 后端参考：[tool-streaming/agent.ts](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/tool-streaming/agent.ts)

- **`custom-streaming`**
  - 展示能力：`progress` / `status` / `file-status` 自定义事件
  - 前端参考：[custom-streaming/index.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/custom-streaming/index.tsx)
  - 组件参考：[ProgressCard.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/custom-streaming/components/ProgressCard.tsx)
  - 组件参考：[StatusBadge.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/custom-streaming/components/StatusBadge.tsx)
  - 组件参考：[FileOperationCard.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/custom-streaming/components/FileOperationCard.tsx)
  - 类型参考：[custom-streaming/types.ts](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/custom-streaming/types.ts)
  - 后端参考：[custom-streaming/agent.ts](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/custom-streaming/agent.ts)

- **`branching-chat`**
  - 展示能力：branch / checkpoint / regenerate / 编辑旧消息
  - 前端参考：[branching-chat/index.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/branching-chat/index.tsx)
  - 组件参考：[BranchSwitcher.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/branching-chat/components/BranchSwitcher.tsx)
  - 后端参考：[branching-chat/agent.ts](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/branching-chat/agent.ts)

- **`session-persistence`**
  - 展示能力：刷新后恢复流、thread 持久化、`reconnectOnMount`
  - 前端参考：[session-persistence/index.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/session-persistence/index.tsx)
  - 后端参考：[session-persistence/agent.ts](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/session-persistence/agent.ts)

- **`parallel-research`**
  - 展示能力：并行研究节点结果面板
  - 前端参考：[parallel-research/index.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/parallel-research/index.tsx)
  - 组件参考：[ResearchCard.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/parallel-research/components/ResearchCard.tsx)
  - 组件参考：[SelectedResearchDisplay.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/parallel-research/components/SelectedResearchDisplay.tsx)
  - 组件参考：[TopicBar.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/parallel-research/components/TopicBar.tsx)
  - 类型参考：[parallel-research/types.ts](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/parallel-research/types.ts)
  - 后端参考：[parallel-research/agent.ts](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/parallel-research/agent.ts)

- **`deepagent`**
  - 展示能力：subagent pipeline、`filterSubagentMessages`、`streamSubgraphs`
  - 前端参考：[deepagent/index.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/deepagent/index.tsx)
  - 组件参考：[SubagentPipeline.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/deepagent/components/SubagentPipeline.tsx)
  - 组件参考：[SubagentCard.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/deepagent/components/SubagentCard.tsx)
  - 后端参考：[deepagent/agent.ts](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/deepagent/agent.ts)
  - 工具参考：[deepagent/tools.ts](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/deepagent/tools.ts)

- **`deepagent-tools`**
  - 展示能力：subagent + tool calls 联合展示
  - 前端参考：[deepagent-tools/index.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/deepagent-tools/index.tsx)
  - 组件参考：[SubagentPipeline.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/deepagent-tools/components/SubagentPipeline.tsx)
  - 组件参考：[SubagentToolCallCard.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/deepagent-tools/components/SubagentToolCallCard.tsx)
  - 组件参考：[SubagentStreamCard.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/deepagent-tools/components/SubagentStreamCard.tsx)
  - 类型参考：[deepagent-tools/types.ts](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/deepagent-tools/types.ts)
  - 后端参考：[deepagent-tools/agent.ts](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/deepagent-tools/agent.ts)

### 建议接入优先级

- **第一优先级**
  - `session-persistence`
  - `tool-streaming`

- **第二优先级**
  - `summarization-agent`
  - `reasoning-agent`

- **第三优先级**
  - `deepagent`
  - `deepagent-tools`

- **第四优先级**
  - `parallel-research`
  - `custom-streaming`

### 共享入口与总参考

- 示例总入口：[examples/ui-react/src/components/Layout.tsx](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/components/Layout.tsx)
- 示例注册表：[examples/ui-react/src/examples/registry.ts](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/src/examples/registry.ts)
- graph 映射：[examples/ui-react/langgraph.json](https://github.com/langchain-ai/langgraphjs/tree/main/examples/ui-react/langgraph.json)

### 验收时的认知边界

- `graph_src_v2` 当前更适合验证：
  - Tool Calls
  - Interrupt / HITL
  - Branch / Regenerate
  - Thread / Reconnect 基础能力
  - Deepagent / Subagent 基础能力

- `graph_src_v2` 当前还不足以完整验证：
  - Summary Messages
  - Reasoning Blocks
  - Tool Progress
  - Custom Event Cards
  - Parallel Research Panel

- 如果后续要完整验证这些专项前端能力，建议在 `graph_src_v2` 里补充：
  - `summarization_demo`
  - `reasoning_demo`
  - `parallel_research_demo`
  - `custom_streaming_demo`

## Going to Production

Once you're ready to go to production, you'll need to update how you connect, and authenticate requests to your deployment. By default, the Agent Chat UI is setup for local development, and connects to your LangGraph server directly from the client. This is not possible if you want to go to production, because it requires every user to have their own LangSmith API key, and set the LangGraph configuration themselves.

### Production Setup

To productionize the Agent Chat UI, you'll need to pick one of two ways to authenticate requests to your LangGraph server. Below, I'll outline the two options:

### Quickstart - API Passthrough

The quickest way to productionize the Agent Chat UI is to use the [API Passthrough](https://github.com/bracesproul/langgraph-nextjs-api-passthrough) package ([NPM link here](https://www.npmjs.com/package/langgraph-nextjs-api-passthrough)). This package provides a simple way to proxy requests to your LangGraph server, and handle authentication for you.

This repository already contains all of the code you need to start using this method. The only configuration you need to do is set the proper environment variables.

```bash
NEXT_PUBLIC_ASSISTANT_ID="agent"
# This should be the deployment URL of your LangGraph server
LANGGRAPH_API_URL="https://my-agent.default.us.langgraph.app"
# This should be the URL of your website + "/api". This is how you connect to the API proxy
NEXT_PUBLIC_API_URL="https://my-website.com/api"
# Your LangSmith API key which is injected into requests inside the API proxy
LANGSMITH_API_KEY="lsv2_..."
```

Let's cover what each of these environment variables does:

- `NEXT_PUBLIC_ASSISTANT_ID`: The ID of the assistant you want to use when fetching, and submitting runs via the chat interface. This still needs the `NEXT_PUBLIC_` prefix, since it's not a secret, and we use it on the client when submitting requests.
- `LANGGRAPH_API_URL`: The URL of your LangGraph server. This should be the production deployment URL.
- `NEXT_PUBLIC_API_URL`: The URL of your website + `/api`. This is how you connect to the API proxy. For the [Agent Chat demo](https://agentchat.vercel.app), this would be set as `https://agentchat.vercel.app/api`. You should set this to whatever your production URL is.
- `LANGSMITH_API_KEY`: Your LangSmith API key to use when authenticating requests sent to LangGraph servers. Once again, do _not_ prefix this with `NEXT_PUBLIC_` since it's a secret, and is only used on the server when the API proxy injects it into the request to your deployed LangGraph server.

For in depth documentation, consult the [LangGraph Next.js API Passthrough](https://www.npmjs.com/package/langgraph-nextjs-api-passthrough) docs.

### Advanced Setup - Custom Authentication

Custom authentication in your LangGraph deployment is an advanced, and more robust way of authenticating requests to your LangGraph server. Using custom authentication, you can allow requests to be made from the client, without the need for a LangSmith API key. Additionally, you can specify custom access controls on requests.

To set this up in your LangGraph deployment, please read the LangGraph custom authentication docs for [Python](https://langchain-ai.github.io/langgraph/tutorials/auth/getting_started/), and [TypeScript here](https://langchain-ai.github.io/langgraphjs/how-tos/auth/custom_auth/).

Once you've set it up on your deployment, you should make the following changes to the Agent Chat UI:

1. Configure any additional API requests to fetch the authentication token from your LangGraph deployment which will be used to authenticate requests from the client.
2. Set the `NEXT_PUBLIC_API_URL` environment variable to your production LangGraph deployment URL.
3. Set the `NEXT_PUBLIC_ASSISTANT_ID` environment variable to the ID of the assistant you want to use when fetching, and submitting runs via the chat interface.
4. Modify the [`useTypedStream`](src/providers/Stream.tsx) (extension of `useStream`) hook to pass your authentication token through headers to the LangGraph server:

```tsx
const streamValue = useTypedStream({
  apiUrl: process.env.NEXT_PUBLIC_API_URL,
  assistantId: process.env.NEXT_PUBLIC_ASSISTANT_ID,
  // ... other fields
  defaultHeaders: {
    Authentication: `Bearer ${addYourTokenHere}`, // this is where you would pass your authentication token
  },
});
```
