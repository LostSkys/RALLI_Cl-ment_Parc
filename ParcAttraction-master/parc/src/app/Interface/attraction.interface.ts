export interface AttractionInterface {
    attraction_id: number;
    nom: string;
    description: string;
    difficulte: number;
    visible: number;
    critiques?: CritiqueInterface[]; 
}

export interface CritiqueInterface {
    critique_id: number;
    attraction_id: number;
    nom: string;
    prenom: string;
    note: number;
    commentaire: string;
    est_anonyme: boolean;
}