// app/page.tsx — The homepage just redirects to the dashboard.
import { redirect } from "next/navigation";

export default function Home() {
  redirect("/dashboard");
}
