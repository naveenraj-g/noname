"use client";

import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { toast } from "sonner";
import { useRouter, useSearchParams } from "next/navigation";
import { Loader2 } from "lucide-react";

import { authClient } from "@/modules/client/auth/betterauth/auth-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export function ResetPassForm() {
  const t = useTranslations("auth.resetPassword");
  const searchParams = useSearchParams();
  const { push } = useRouter();
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    if (searchParams) {
      setToken(searchParams.get("token"));
    }
  }, [searchParams]);

  const resetPassFormSchema = z.object({
    password: z
      .string()
      .min(8, t("form.validation.min"))
      .max(16, t("form.validation.max")),
  });

  type ResetPassForm = z.infer<typeof resetPassFormSchema>;

  const form = useForm<ResetPassForm>({
    resolver: zodResolver(resetPassFormSchema),
    defaultValues: { password: "" },
  });

  const {
    formState: { isSubmitting },
  } = form;

  async function onSubmit(values: ResetPassForm) {
    if (!token) {
      toast(t("toast.errorTitle"), {
        description: (
          <span className="dark:text-zinc-400">
            {t("toast.errorDescription")}
          </span>
        ),
      });
      return;
    }

    const { password } = values;
    await authClient.resetPassword(
      {
        newPassword: password,
        token,
      },
      {
        onSuccess: () => {
          toast(t("toast.success"));
          push("/signin");
        },
        onError: (ctx: any) => {
          toast(t("toast.errorTitle"), {
            description: (
              <span className="dark:text-zinc-400">{ctx.error.message}</span>
            ),
          });
        },
      }
    );
  }

  return (
    <Card className="w-[400px]">
      <CardHeader>
        <CardTitle className="card-title">{t("title")}</CardTitle>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("form.label")}</FormLabel>
                  <FormControl>
                    <Input
                      placeholder={t("form.placeholder")}
                      {...field}
                      type="password"
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="w-full mx-auto">
              <Button
                type="submit"
                className="w-full cursor-pointer"
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="animate-spin" />{" "}
                    {t("form.button.loading")}
                  </>
                ) : (
                  t("form.button.default")
                )}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
}
