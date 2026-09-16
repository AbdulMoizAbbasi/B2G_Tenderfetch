import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  try {
    const filePath = path.join(
      process.cwd(),
      "..",
      "data",
      "relevant_tenders.json"
    );

    if (!fs.existsSync(filePath)) {
      return NextResponse.json(
        {
          error: "Tender data file not found.",
          path: filePath,
        },
        { status: 404 }
      );
    }

    const fileContent = fs.readFileSync(
      filePath,
      "utf-8"
    );

    const tenders = JSON.parse(fileContent);

    if (!Array.isArray(tenders)) {
      return NextResponse.json(
        {
          error: "Tender data must be an array.",
        },
        { status: 500 }
      );
    }

    return NextResponse.json(tenders);
  } catch (error) {
    console.error("Failed to load tender data:", error);

    return NextResponse.json(
      {
        error: "Failed to load tender data.",
      },
      { status: 500 }
    );
  }
}