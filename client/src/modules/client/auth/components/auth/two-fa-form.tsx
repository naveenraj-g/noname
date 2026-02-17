"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSlot,
} from "@/components/ui/input-otp";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import { authClient } from "@/modules/client/auth/betterauth/auth-client";
import { useTranslations } from "next-intl";

const TwoFaForm = () => {
  const t = useTranslations("auth.twofa");
  const router = useRouter();

  const FormSchema = z.object({
    otp: z.string().min(6, {
      message: "Your one-time password must be 6 characters.",
    }),
  });

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
    defaultValues: {
      otp: "",
    },
  });

  const {
    formState: { isSubmitting },
  } = form;

  async function onSubmitOtp(values: z.infer<typeof FormSchema>) {
    await authClient.twoFactor.verifyOtp(
      { code: values.otp },
      {
        onSuccess() {
          toast("Verified Successfully!");
          router.push("/bezs");
        },
        onError(ctx) {
          toast("An error occurred!", {
            description: ctx.error.message,
          });
        },
      }
    );
  }

  return (
    <Card className="max-w-96 mx-auto">
      <CardHeader>
        <CardTitle>{t("title")}</CardTitle>
        <CardDescription>{t("description")}</CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmitOtp)} className="space-y-6">
            <FormField
              control={form.control}
              name="otp"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>{t("form.label")}</FormLabel>
                  <FormControl>
                    <InputOTP maxLength={6} {...field}>
                      <InputOTPGroup>
                        <InputOTPSlot index={0} />
                        <InputOTPSlot index={1} />
                        <InputOTPSlot index={2} />
                        <InputOTPSlot index={3} />
                        <InputOTPSlot index={4} />
                        <InputOTPSlot index={5} />
                      </InputOTPGroup>
                    </InputOTP>
                  </FormControl>
                  <FormDescription>{t("form.helper")}</FormDescription>
                  <FormMessage />
                  <div>
                    <Button
                      type="button"
                      variant="link"
                      className="cursor-pointer pl-0 underline hover:text-blue-600"
                      onClick={async () => {
                        const { data, error } =
                          await authClient.twoFactor.sendOtp();

                        if (error) {
                          toast(t("toast.errorTitle"), {
                            description:
                              error.message || t("toast.errorDescription"),
                          });
                          return;
                        }

                        toast(t("toast.otpSentTitle"), {
                          description: (
                            <span>{t("toast.otpSentDescription")}</span>
                          ),
                        });
                      }}
                    >
                      {t("form.requestOtp")}
                    </Button>
                  </div>
                </FormItem>
              )}
            />
            <Button
              type="submit"
              className="cursor-pointer"
              disabled={isSubmitting}
            >
              {isSubmitting ? t("form.submitting") : t("form.submit")}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  );
};

export default TwoFaForm;
