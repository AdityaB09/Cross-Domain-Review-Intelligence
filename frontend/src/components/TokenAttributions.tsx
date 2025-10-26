"use client";

import TokenAttributionsPills from "./TokenAttributionPills";

export type Attribution = {
  token: string;
  score: number;
};

export default function TokenAttributions(props: { tokens: Attribution[] }) {
  return <TokenAttributionsPills tokens={props.tokens} />;
}
