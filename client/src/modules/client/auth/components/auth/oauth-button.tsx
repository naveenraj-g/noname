"use client";

import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { RiGoogleFill, RiGithubFill } from "@remixicon/react";
import { useState } from "react";
import { toast } from "sonner";
import { authClient } from "@/modules/client/auth/betterauth/auth-client";
import { cn } from "@/lib/utils";

type Props = {
  oauthName: "google" | "github";
  label: string;
  isFormSubmitting: boolean;
  className?: string;
};

const OauthButton = ({
  oauthName,
  label,
  isFormSubmitting,
  className,
}: Props) => {
  const [isAuthLoading, setIsAuthLoading] = useState(false);

  return (
    <Button
      variant="outline"
      disabled={isAuthLoading || isFormSubmitting}
      className={cn(
        "flex-1 items-center justify-center cursor-pointer border-2",
        className
      )}
      onClick={async () => {
        setIsAuthLoading(true);
        await authClient.signIn.social(
          {
            provider: oauthName,
            callbackURL: `/bezs`,
            newUserCallbackURL: "/set-username",
          },
          {
            onError(ctx) {
              toast("An error occurred!", {
                description: (
                  <span className="dark:text-zinc-400">
                    {ctx.error.message}
                  </span>
                ),
              });
            },
            onRequest() {
              setIsAuthLoading(true);
            },
            onResponse() {
              setIsAuthLoading(false);
            },
          }
        );
      }}
    >
      <span className="pointer-events-none">
        {!isAuthLoading ? (
          oauthName === "google" ? (
            <RiGoogleFill className="" size={18} aria-hidden="true" />
          ) : (
            <RiGithubFill size={18} aria-hidden="true" />
          )
        ) : (
          <Loader2 className="animate-spin" />
        )}
      </span>
      {label}
    </Button>
  );
};

export default OauthButton;
