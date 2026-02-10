const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ValorarResponse {
  estrellas: number;
  puntuacion_media: number;
  valoracion: string;
  estrellas_emoji: string;
}

export interface ResenaItem {
  id: string;
  comments: string;
  reviewer_name: string;
  date: string;
  estrellas: number;
  puntuacion_media: number;
  valoracion: string;
  estrellas_emoji: string;
}

export async function valorarResena(texto: string): Promise<ValorarResponse> {
  const res = await fetch(`${API_URL}/api/valorar`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail || "Error al valorar");
  }
  return res.json();
}

export async function fetchResenas(limite = 200): Promise<ResenaItem[]> {
  const res = await fetch(`${API_URL}/api/resenas?limite=${limite}`);
  if (!res.ok) throw new Error("Error al cargar reseñas");
  const data = await res.json();
  return data.resenas ?? [];
}

export async function healthCheck(): Promise<{ ok: boolean; modelo_cargado: boolean }> {
  const res = await fetch(`${API_URL}/api/health`);
  if (!res.ok) throw new Error("API no disponible");
  return res.json();
}
