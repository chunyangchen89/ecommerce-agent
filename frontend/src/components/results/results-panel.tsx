"use client";

import type { QueryResponse } from "@/lib/types";
import { motion } from "motion/react";
import { IntentBadge } from "./intent-badge";
import { AnswerCard } from "./answer-card";
import { SqlSection } from "./sql-section";
import { DataTable } from "./data-table";
import { RagSection } from "./rag-section";

interface ResultsPanelProps {
  data: QueryResponse;
}

const fadeUp = {
  initial: { opacity: 0, y: 40 },
  whileInView: { opacity: 1, y: 0 },
  viewport: { once: true, margin: "-50px" },
  transition: { duration: 0.5, ease: "easeOut" },
};

export function ResultsPanel({ data }: ResultsPanelProps) {
  return (
    <div className="mx-auto max-w-3xl space-y-4">
      {data.intent && (
        <motion.div {...fadeUp}>
          <IntentBadge intent={data.intent} />
        </motion.div>
      )}
      <motion.div {...fadeUp} transition={{ ...fadeUp.transition, delay: 0.1 }}>
        <AnswerCard answer={data.answer} />
      </motion.div>
      {data.sql && (
        <motion.div {...fadeUp} transition={{ ...fadeUp.transition, delay: 0.2 }}>
          <SqlSection sql={data.sql} />
        </motion.div>
      )}
      {data.sql_result && data.sql_result.length > 0 && (
        <motion.div {...fadeUp} transition={{ ...fadeUp.transition, delay: 0.3 }}>
          <DataTable data={data.sql_result} />
        </motion.div>
      )}
      {data.rag_context && (
        <motion.div {...fadeUp} transition={{ ...fadeUp.transition, delay: 0.4 }}>
          <RagSection context={data.rag_context} />
        </motion.div>
      )}
    </div>
  );
}
