# PILOT-001 — Baseline Summary (v0.1.4, information parity)

The lesson's central reframe is to stop asking which task can be automated and to start asking what system of agents can handle an entire function. Starting from outcomes rather than from a to-do list is what makes the work compound instead of producing one-off automations.

The operating principle is to use humans for judgment and agents for execution.

Three things are distinguished. A chatbot answers a question. An automation runs a fixed playbook and breaks when something unexpected happens. An agent has a goal, reasons through multiple steps, uses tools to act, and adapts when conditions change.

The market context given is that the agents market is on track to hit $50 billion by 2030 and that Gartner expects 60% of brands to use agentic AI by 2028, but also that over 40% of agent projects will be cancelled by the end of 2027 because teams rushed in without a plan, a clear outcome or governance. Building the wrong agent is said to be just as expensive as building nothing.

Every working agent, simple or complex, is said to have the same five building blocks, and the whole thing falls apart if any one of them is missing or weak.

The first block is the brain: the underlying language model doing the reasoning. The lesson holds that the model matters less than people think.

The second block is the instructions, the system prompt, described as the job description for the agent: who it is, what it does, what it is allowed to do and what it must never do. Weak instructions equal a weak agent, and the system prompt is presented as 80% of the quality of what comes out.

The third block is the tools, which is what the agent can actually do — web search, CRM read and write, email send, calendar actions. Without tools the agent is just a chatbot with a fancy hat.

The fourth block is memory: short-term within the conversation, and long-term for brand guidelines, product information, customer context and past sessions.

The fifth block is presented as non-negotiable: a human in the loop. Any agent that touches money, messaging or the customer needs a review step in the first 30 days, with no exceptions.

Three agents are proposed as the first ones worth building: an intelligence agent at the top of the funnel that monitors competitors and delivers a plain English briefing; a content production agent in the middle that turns one approved long-form input into a multi-channel cascade queued for human review; and a revenue operations agent at the bottom that enriches and qualifies leads, scores them against the ICP and flags hot ones to a human rep. They chain: the first tells you what to say, the second turns it into distribution, the third converts the demand.

On platform choice, the lesson says it matters less than people think and that what matters is picking one and shipping something.

The options are framed by where the team already is. HubSpot Breeze for teams already on HubSpot Professional or Enterprise, with near-zero setup overhead. Claude for no-code research and content work, which is what the live build uses. Gumloop for visual thinkers who want drag-and-drop. Zapier Agents for teams already on Zapier doing light operational work. OpenClaw is treated separately: open source, runs locally, controls the computer directly, and unlocks tools with no API — but a security audit found that over a third of its skills had at least one flaw, so it is presented as a last resort.

The build starts with the outcome. Before opening any tool, write down three things: what information you will give, what output you want back, and clear boundaries — what the agent is never allowed to do. The most common mistake is opening the platform before defining what you actually want, which ends in automating a task instead of owning an outcome.

The worked example uses three competitor URLs as the input, a structured briefing posted to a Slack channel every Monday morning as the output, and boundaries that the agent never sends external emails, never posts outside the designated channel and never stores contact data.

The instructions are written with the ROBOT framework: role, objective, boundaries, output, tone. Every great agent prompt is said to have all five, every line in the prompt is doing a job, and the more specific it is the better the result — vague instructions equal vague output every time.

Then the platform is chosen and the tools connected. What a platform can connect to is one of the first things to look at, because integrations are what turn a chat window into something that does work. The example connects exactly two: web search, toggled on so it pulls live competitor data, and Slack, so it posts the briefing to the channel. Running it automatically every Monday is described as an optional Zapier schedule added on top.

Next the agent is fed memory, which is what separates a generic bot from one that understands the business: context about who you are, who you serve and what good looks like. In the example this is channel context — audience description, competitor list, content pillars and goal — and the lesson notes it would be a product catalogue and personas for e-commerce, an ICP and positioning doc for B2B, or a client brief for an agency.

Then it is tested, broken and fixed. Run it three to five times; every time it produces something off-brand or surface level, go back to the system prompt and tighten it, and write down every failure as a fix list.

Then a human is added in the loop for the first 30 days, reviewing every output before it goes anywhere; after 30 days, if it is consistently solid, the review can be loosened.

Finally it is measured with two questions: is it saving at least two hours a week, and is the output better than what you would produce manually. If both are yes, expand it; if either is no, go back and rebuild it.

The lesson includes a live build of the intelligence agent in Claude — project, instructions, memory, two tools, then a test — completed in 6 minutes and 19 seconds.

The closing advice is not to build everything at once but to start with one gap — the workflow that costs the team the most time every week.
