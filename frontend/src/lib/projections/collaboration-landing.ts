/**
 * Local Collaboration & Sharing fixture for ui_18_collaboration.md / .svg.
 * Presentation-only. No peer execution channel; comments ≠ critiques.
 * Sharing permissions and co-edit sessions require authorized actions.
 */

import type { ScreenLabels } from "./screen-labels";

export type CollaborationShareKind = "swarm" | "agent" | "pattern";

export interface CollaborationSharedItem {
  readonly id: string;
  readonly kind: CollaborationShareKind;
  readonly title: string;
  readonly detail: string;
  readonly owner: string;
  readonly scope: string;
  readonly actions: readonly string[];
}

export interface CollaborationShareMember {
  readonly id: string;
  readonly initials: string;
  readonly name: string;
  readonly role: string;
}

export interface CollaborationContributeItem {
  readonly id: string;
  readonly title: string;
  readonly detail: string;
  readonly cta: string;
}

export interface CollaborationSession {
  readonly id: string;
  readonly title: string;
  readonly presence: string;
  readonly editors: readonly string[];
  readonly canJoin: boolean;
}

export interface CollaborationActivityItem {
  readonly id: string;
  readonly initials: string;
  readonly text: string;
  readonly time: string;
}

export interface CollaborationLandingView {
  readonly labels: ScreenLabels;
  readonly eyebrow: string;
  readonly title: string;
  readonly description: string;
  readonly searchPlaceholder: string;
  readonly tabs: readonly string[];
  readonly sharedItems: readonly CollaborationSharedItem[];
  readonly shareModal: {
    readonly title: string;
    readonly members: readonly CollaborationShareMember[];
    readonly link: string;
    readonly note: string;
  };
  readonly contributions: readonly CollaborationContributeItem[];
  readonly impact: string;
  readonly sessions: readonly CollaborationSession[];
  readonly teamActivity: readonly CollaborationActivityItem[];
  readonly proposalQueue: readonly {
    readonly id: string;
    readonly title: string;
    readonly assignee: string;
    readonly status: string;
  }[];
  readonly critiqueNote: string;
  readonly footerNote: string;
}

export const LOCAL_COLLABORATION_LANDING: CollaborationLandingView = {
  labels: {
    "search_shared_items": "Search shared items",
    "no_shared_items_match_the_search": "No shared items match the search.",
    "add_people_or_teams": "Add people or teams",
    "link_sharing": "Link sharing",
    "contribute_back_to_commons": "Contribute Back to Commons",
    "live_co_editing": "Live Co-Editing",
    "team_activity": "Team Activity",
    "proposal_review_workflows": "Proposal Review Workflows",
    "add_people_or_teams_2": "Add people or teams…",
    "collaboration_and_sharing_hub": "Collaboration and sharing hub",
    "share_lists": "Share lists",
    "share_modal": "Share modal",
    "permission_levels": "Permission levels",
  },
  eyebrow: "COLLABORATION",
  title: "Collaboration & Sharing Hub",
  description:
    "Share swarms, contribute back to commons, manage team workflows & live co-editing.",
  searchPlaceholder: "Search shared items…",
  tabs: ["Shared with me", "My shares"],
  sharedItems: [
    {
      id: "i1",
      kind: "swarm",
      title: "Wuxia Short (Swarm)",
      detail: "Parallel + Verify v1.4 · 8 agents",
      owner: "Ava Lin",
      scope: "Team: Video",
      actions: ["Open", "Duplicate"],
    },
    {
      id: "i2",
      kind: "agent",
      title: "video.judge v3.0 (Common Agent)",
      detail: "Common · 97% success · 31.2k runs",
      owner: "Ecosystem",
      scope: "Public",
      actions: ["Add", "Propose"],
    },
    {
      id: "i3",
      kind: "pattern",
      title: "Dynamic Router Pattern (Template)",
      detail: "Pattern · 89% · 112 swarms",
      owner: "Bob Wu",
      scope: "Content team",
      actions: ["Open"],
    },
  ],
  shareModal: {
    title: "Share Wuxia Short",
    members: [
      { id: "m1", initials: "NH", name: "You", role: "Owner" },
      { id: "m2", initials: "AL", name: "Ava Lin", role: "Editor" },
    ],
    link: "https://caso.local/s/wuxia-short-7f2a",
    note: "Access controlled server-side · link can be revoked anytime. Permissions: view, comment, edit — never peer execution authority.",
  },
  contributions: [
    {
      id: "c1",
      title: "video.copywriter",
      detail: "Fork of Common v2.3 · used 312 times · 93% success",
      cta: "Propose to Registry",
    },
    {
      id: "c2",
      title: "Improved video.trendintelligence",
      detail: "Fork of v1.9 · +5% quality · 12 swarm runs verified",
      cta: "Create Proposal",
    },
  ],
  impact:
    "18 contributions merged · $3.1k savings driven · rank #12",
  sessions: [
    {
      id: "s1",
      title: "Wuxia Short — Execute",
      presence: "2 editing now",
      editors: ["NH", "AL"],
      canJoin: true,
    },
    {
      id: "s2",
      title: "Brand Spot — Execute",
      presence: "No one editing · last edit 2h ago",
      editors: [],
      canJoin: false,
    },
  ],
  teamActivity: [
    {
      id: "t1",
      initials: "AL",
      text: "Commented on video.judge proposal (not a critique)",
      time: "12m",
    },
    {
      id: "t2",
      initials: "BW",
      text: "Assigned proposal review to NH",
      time: "40m",
    },
    {
      id: "t3",
      initials: "NH",
      text: "Shared Wuxia Short with Video team",
      time: "1h",
    },
    {
      id: "t4",
      initials: "MC",
      text: "Meta-critic opened improvement discussion",
      time: "2h",
    },
  ],
  proposalQueue: [
    {
      id: "p1",
      title: "video.editor → v3.0",
      assignee: "NH",
      status: "Awaiting review",
    },
    {
      id: "p2",
      title: "video.trendintelligence fork proposal",
      assignee: "AL",
      status: "Discussion",
    },
  ],
  critiqueNote:
    "Comments are not interchangeable with critiques. A critique has source/target, severity, rubric/evidence, status, and authorized delivery relationship. Shared graph editing retains revision/provenance and approval/audit evidence; collaborators cannot alter historical run or signature data.",
  footerNote:
    "Local preview collaboration · no peer execution channel · Share / Join session / Propose require authorized workspace actions. Real-time CRDT/Yjs deferred.",
};
