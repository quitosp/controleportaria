export function urlEhSegura(returnUrl: string | null | undefined, hostsPermitidos: string[] = []): string {
  if (!returnUrl) return "/";
  try {
    if (returnUrl.startsWith("/") && !returnUrl.startsWith("//")) return returnUrl;
    const u = new URL(returnUrl);
    if (hostsPermitidos.includes(u.host)) return returnUrl;
  } catch { /* invalid url */ }
  return "/";
}

export function sanitizarHtmlSeguro(html: string): string {
  // Stub: instale DOMPurify para sanitizacao real
  // import DOMPurify from "isomorphic-dompurify";
  // return DOMPurify.sanitize(html);
  return html.replace(/<script[^>]*>[\s\S]*?<\/script>/gi, "")
             .replace(/on\w+="[^"]*"/gi, "")
             .replace(/javascript:/gi, "");
}
