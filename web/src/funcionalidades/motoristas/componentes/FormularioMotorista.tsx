"use client";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { Button } from "@/compartilhados/componentes/ui/button";
import { Input } from "@/compartilhados/componentes/ui/input";
import { Label } from "@/compartilhados/componentes/ui/label";
import { salvarMotoristaSchema, type SalvarMotorista } from "../tipos";
import { useSalvarMotorista } from "../ganchos";

export function FormularioMotorista({ aoSalvar }: { aoSalvar?: () => void } = {}) {
  const { register, handleSubmit, reset, formState: { errors } } = useForm<SalvarMotorista>({
    resolver: zodResolver(salvarMotoristaSchema),
  });
  const mutation = useSalvarMotorista();

  return (
    <form
      onSubmit={handleSubmit(d =>
        mutation.mutate(d, {
          onSuccess: (resp) => {
            if (!resp.success) { toast.error(resp.message); return; }
            toast.success(resp.message);
            reset();
            aoSalvar?.();
          },
          onError: () => toast.error("Erro ao salvar"),
        })
      )}
      className="space-y-4"
    >
      <div className="space-y-2">
        <Label htmlFor="nome">Nome</Label>
        <Input id="nome" type="text" {...register("nome")} />
        {errors.nome && <p className="text-sm text-destructive">{errors.nome.message}</p>}
      </div>
      <Button type="submit" disabled={mutation.isPending} className="w-full">
        {mutation.isPending ? "Salvando..." : "Salvar"}
      </Button>
    </form>
  );
}
