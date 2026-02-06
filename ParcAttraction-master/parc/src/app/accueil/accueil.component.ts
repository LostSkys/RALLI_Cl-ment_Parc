import { Component, OnInit } from '@angular/core';
import { AttractionService } from '../Service/attraction.service';
import { CommonModule } from '@angular/common';
import { Observable } from 'rxjs';
import { AttractionInterface } from '../Interface/attraction.interface';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { CritiqueDialogComponent } from '../critique-dialog/critique-dialog.component';

@Component({
  selector: 'app-accueil',
  standalone: true,
  imports: [
    CommonModule, 
    MatCardModule, 
    MatButtonModule, 
    MatIconModule,
    MatProgressSpinnerModule,
    MatDialogModule
  ],
  templateUrl: './accueil.component.html',
  styleUrl: './accueil.component.scss'
})
export class AccueilComponent implements OnInit {

  public attractions: Observable<AttractionInterface[]>;
  public currentLang: string = 'fr';

  constructor(
    public attractionService: AttractionService,
    private dialog: MatDialog
  ) {
    this.attractions = this.attractionService.getAllVisibleAttractionWithCritiques();
  }

  ngOnInit() {
    // Détecter la langue du navigateur
    const browserLang = navigator.language.split('-')[0];
    this.currentLang = ['fr', 'en'].includes(browserLang) ? browserLang : 'fr';
  }

  switchLanguage(lang: string) {
    this.currentLang = lang;
    // La gestion complète de i18n se fait au niveau du build Angular
    // Pour un changement dynamique, il faudrait recharger l'app avec la bonne locale
    console.log('Langue sélectionnée:', lang);
    // TODO: Implémenter le rechargement avec la bonne locale
  }

  ouvrirDialogueCritique(attraction: AttractionInterface) {
    const dialogRef = this.dialog.open(CritiqueDialogComponent, {
      width: '500px',
      data: { attraction }
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.attractionService.postCritique(result).subscribe({
          next: () => {
            alert($localize`:@@avisMerci:Merci pour votre avis !`);
            // Recharger les attractions pour afficher la nouvelle critique
            this.attractions = this.attractionService.getAllVisibleAttractionWithCritiques();
          },
          error: (err) => {
            console.error('Erreur lors de l\'envoi de la critique:', err);
            alert($localize`:@@avisErreur:Erreur lors de l'envoi de votre avis.`);
          }
        });
      }
    });
  }
}