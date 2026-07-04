import "server-only";
import { cert, getApps, initializeApp } from "firebase-admin/app";
import { getFirestore } from "firebase-admin/firestore";

function buildDb() {
  if (!getApps().length) {
    const raw = process.env.FIREBASE_SERVICE_ACCOUNT_JSON;
    if (!raw) {
      throw new Error("FIREBASE_SERVICE_ACCOUNT_JSON is not set in frontend/.env.local");
    }
    initializeApp({ credential: cert(JSON.parse(raw)) });
  }
  return getFirestore();
}

const globalForFirestore = globalThis as unknown as {
  firestoreDb: ReturnType<typeof getFirestore> | undefined;
};

export const db = globalForFirestore.firestoreDb ?? buildDb();

if (process.env.NODE_ENV !== "production") {
  globalForFirestore.firestoreDb = db;
}
