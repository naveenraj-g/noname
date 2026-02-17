"use server";

import { prismaMain } from "../../prisma/prisma";

const DEFAULT_ORG_SLUG = "bezs-org";
const DEFAULT_ROLE_NAME = "patient";
const DEFAULT_MEMBER_ROLE = "member";

export async function mapNewUserToOrg(userId: string) {
  await prismaMain.$transaction(async (tx) => {
    const org = await tx.organization.findUnique({
      where: { slug: DEFAULT_ORG_SLUG },
    });

    if (!org) return;

    const isUserInOrg = await tx.member.findFirst({
      where: {
        userId,
      },
    });

    if (isUserInOrg) return;

    const defaultOrg = await tx.organization.findUnique({
      where: {
        slug: DEFAULT_ORG_SLUG,
      },
    });

    if (!defaultOrg) return;

    await tx.member.create({
      data: {
        userId,
        organizationId: defaultOrg.id,
        role: DEFAULT_MEMBER_ROLE,
      },
    });

    const defaultRole = await tx.role.findUnique({
      where: {
        name: DEFAULT_ROLE_NAME,
      },
    });

    if (!defaultRole) return;

    await tx.rBAC.create({
      data: {
        userId,
        roleId: defaultRole.id,
        organizationId: defaultOrg.id,
        defaultRedirectUrl: "/bezs/telemedicine/patient/appointments/intake",
      },
    });
  });
}
