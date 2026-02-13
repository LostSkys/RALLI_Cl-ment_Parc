export interface CritiqueInterface {
    critique_id?: number;
    attraction_id: number;
    nom: string;
    prenom: string;
    note: number;
    commentaire: string;
    est_anonyme: boolean;
    created_at?: string;
}