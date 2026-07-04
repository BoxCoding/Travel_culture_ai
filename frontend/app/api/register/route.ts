import { NextRequest, NextResponse } from "next/server";
import bcrypt from "bcryptjs";
import { createUser, findUserByEmail } from "@/lib/users";

export async function POST(request: NextRequest) {
  let body: { name?: string; email?: string; password?: string };
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ detail: "Invalid JSON body" }, { status: 400 });
  }

  const { name, email, password } = body;

  if (!email || !password) {
    return NextResponse.json(
      { detail: "Email and password are required" },
      { status: 400 }
    );
  }

  if (password.length < 8) {
    return NextResponse.json(
      { detail: "Password must be at least 8 characters" },
      { status: 400 }
    );
  }

  const normalizedEmail = email.toLowerCase().trim();

  const existing = await findUserByEmail(normalizedEmail);
  if (existing) {
    return NextResponse.json(
      { detail: "An account with that email already exists" },
      { status: 409 }
    );
  }

  const passwordHash = await bcrypt.hash(password, 10);

  const user = await createUser({
    name: name?.trim() || null,
    email: normalizedEmail,
    passwordHash,
  });

  return NextResponse.json(
    { user: { id: user.id, email: user.email, name: user.name } },
    { status: 201 }
  );
}
