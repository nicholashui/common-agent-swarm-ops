import { redirect } from "next/navigation";

function LegacyCanvasPage(): never {
  redirect("/");
}

export default LegacyCanvasPage;
