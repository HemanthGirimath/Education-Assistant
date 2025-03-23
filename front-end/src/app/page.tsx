"use client";

import { useState } from "react";
import PDFUploader from "@/components/PDFUploader";
import ChatInterface from "@/components/ChatInterface";

export default function Home() {
  const [filename, setFilename] = useState<string | null>(null);

  return (
    <main className="container mx-auto p-6">
      <h1 className="text-xl font-bold">Education App</h1>
      <PDFUploader onUpload={(filename) => setFilename(filename)} />
      {filename && <ChatInterface filename={filename} />}
    </main>
  );
}
