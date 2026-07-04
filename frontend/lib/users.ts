import "server-only";
import { randomUUID } from "crypto";
import { db } from "@/lib/firebase-admin";

export interface UserRecord {
  id: string;
  name: string | null;
  email: string;
  passwordHash: string;
  createdAt: string;
}

function usersCollection() {
  return db.collection("users");
}

export async function findUserByEmail(email: string): Promise<UserRecord | null> {
  const doc = await usersCollection().doc(email).get();
  if (!doc.exists) return null;
  return doc.data() as UserRecord;
}

export async function createUser(data: {
  name: string | null;
  email: string;
  passwordHash: string;
}): Promise<UserRecord> {
  const record: UserRecord = {
    id: randomUUID(),
    name: data.name,
    email: data.email,
    passwordHash: data.passwordHash,
    createdAt: new Date().toISOString(),
  };
  await usersCollection().doc(data.email).set(record);
  return record;
}
