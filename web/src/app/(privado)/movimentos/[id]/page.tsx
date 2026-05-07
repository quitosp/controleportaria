import { DetalheMovimento } from "@/funcionalidades/movimentos/detalhe";
type Props = { params: Promise<{ id: string }> };
export default async function Page({ params }: Props) {
  const { id } = await params;
  return <DetalheMovimento id={id} />;
}
