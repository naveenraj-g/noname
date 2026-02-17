"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { authClient } from "@/modules/client/auth/betterauth/auth-client";
import { useTranslations } from "next-intl";

const EmailVerificationComp = ({ email }: { email: string }) => {
  const t = useTranslations();

  return (
    <Card className="m-4">
      <CardHeader>
        <CardTitle>{t("title")}</CardTitle>
      </CardHeader>
      <CardContent>
        <p>
          {t("message")} {t("resendPrompt")}{" "}
          <span
            className="link cursor-pointer underline"
            onClick={async () => {
              try {
                await authClient.sendVerificationEmail({
                  email,
                  callbackURL: "/bezs",
                });
                toast(t("toast.success"));
              } catch (error) {
                toast(t("toast.error"), {
                  description: `${error}`,
                });
              }
            }}
          >
            {t("resendLink")}
          </span>
        </p>
      </CardContent>
    </Card>
  );
};

export default EmailVerificationComp;
