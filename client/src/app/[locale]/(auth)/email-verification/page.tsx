import EmailVerificationComp from "@/modules/client/auth/components/auth/email-verification-comp";
import { redirect } from "@/i18n/navigation";
import { getLocale } from "next-intl/server";

const EmailVerification = async ({
  searchParams,
}: {
  searchParams: Promise<{ email?: string }>;
}) => {
  const locale = await getLocale();
  const email = (await searchParams)?.email || "";

  if (!email) {
    redirect({ href: "/signin", locale });
  }

  return <EmailVerificationComp email={email} />;
};

export default EmailVerification;
