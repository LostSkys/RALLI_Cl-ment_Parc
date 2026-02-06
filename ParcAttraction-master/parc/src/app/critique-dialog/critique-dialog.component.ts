import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatIconModule } from '@angular/material/icon';
import { AttractionInterface } from '../Interface/attraction.interface';

@Component({
  selector: 'app-critique-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatCheckboxModule,
    MatIconModule
  ],
  templateUrl: './critique-dialog.component.html',
  styleUrl: './critique-dialog.component.scss'
})
export class CritiqueDialogComponent {
  critiqueForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<CritiqueDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: { attraction: AttractionInterface }
  ) {
    this.critiqueForm = this.fb.group({
      nom: ['', Validators.required],
      prenom: ['', Validators.required],
      note: [null, [Validators.required, Validators.min(1), Validators.max(5)]],
      commentaire: ['', Validators.required],
      est_anonyme: [false]
    });

    // Désactiver nom/prénom si anonyme
    this.critiqueForm.get('est_anonyme')?.valueChanges.subscribe(isAnonymous => {
      if (isAnonymous) {
        this.critiqueForm.get('nom')?.setValue('Anonyme');
        this.critiqueForm.get('prenom')?.setValue('');
        this.critiqueForm.get('nom')?.disable();
        this.critiqueForm.get('prenom')?.disable();
      } else {
        this.critiqueForm.get('nom')?.enable();
        this.critiqueForm.get('prenom')?.enable();
        if (this.critiqueForm.get('nom')?.value === 'Anonyme') {
          this.critiqueForm.get('nom')?.setValue('');
        }
      }
    });
  }

  setNote(note: number) {
    this.critiqueForm.patchValue({ note });
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  onSubmit(): void {
    if (this.critiqueForm.valid) {
      const formValue = this.critiqueForm.getRawValue(); // getRawValue pour inclure les champs disabled
      const critique = {
        attraction_id: this.data.attraction.attraction_id,
        nom: formValue.nom,
        prenom: formValue.prenom,
        note: formValue.note,
        commentaire: formValue.commentaire,
        est_anonyme: formValue.est_anonyme
      };
      this.dialogRef.close(critique);
    }
  }
}