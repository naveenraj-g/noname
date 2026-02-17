import { getRequestConfig } from "next-intl/server";
import { hasLocale } from "next-intl";
import { routing } from "./routing";
import path from "path";
import fs from "fs";

export default getRequestConfig(async ({ requestLocale }) => {
  // Typically corresponds to the `[locale]` segment
  const requested = await requestLocale;
  const locale = hasLocale(routing.locales, requested)
    ? requested
    : routing.defaultLocale;

  // Path to locale folder
  const localeDir = path.join(process.cwd(), "src", "messages", locale);

  // Read all JSON files in that locale folder
  const files = fs.readdirSync(localeDir).filter((f) => f.endsWith(".json"));

  // Merge all files into one object
  const messages = files.reduce((acc, file) => {
    const filePath = path.join(localeDir, file);
    const buffer = fs.readFileSync(filePath);
    const content = JSON.parse(buffer.toString("utf-8"));
    // const content = JSON.parse(fs.readFileSync(filePath, "utf-8"));
    return { ...acc, ...content };
  }, {});

  // console.log({ messages });

  return {
    locale,
    // messages: (await import(`../messages/${locale}.json`)).default,
    messages: messages,
  };
});
