import { Component, OnInit } from '@angular/core';
import { MessageService } from 'primeng/api';
import { ConfirmationService } from 'primeng/api';
import { TableModule } from 'primeng/table';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { CalendarModule } from 'primeng/calendar';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { DialogModule } from 'primeng/dialog';
import { CommonModule } from '@angular/common';
import { ToastModule } from 'primeng/toast';
import { CardModule } from 'primeng/card';
import { ToolbarModule } from 'primeng/toolbar';
import { DatePipe } from '@angular/common';
import { DeleteApiLicensePlatesByLicensePlateIdData, DeleteApiLicensePlatesByLicensePlateIdResponse, GetApiLicensePlatesResponse, LicensePlateCreateResponse, LicensePlateRequest, LicensePlateResponse, LicensePlatesService, MessageResponse, PutApiLicensePlatesByLicensePlateIdResponse } from '../../../rest-api';
import { Observable, catchError, map } from 'rxjs';

// Define the LicensePlate interface
interface LicensePlate {
  id: string;
  licensePlate: string;
  validFrom: Date;
  validTo: Date;
}


@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule, FormsModule, ReactiveFormsModule, TableModule, ConfirmDialogModule,
    CalendarModule, DialogModule, ToastModule, CardModule, ToolbarModule
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss'],
})
export class DashboardComponent implements OnInit {
  licensePlatesTable: LicensePlate[] = [];
  filteredLicensePlates: LicensePlate[] = [];
  selectedLicensePlate!: LicensePlate;
  dialogLicensePlate!: LicensePlate;
  showDialog!: boolean;
  submitted!: boolean;
  licensePlateForm!: FormGroup;
  globalFilter: string = '';

  constructor(
    private messageService: MessageService,
    private confirmationService: ConfirmationService,
    private formBuilder: FormBuilder,
    private datePipe: DatePipe,
    private licensePlatesService: LicensePlatesService,

  ) { }

  ngOnInit(): void {
    this.licensePlateForm = this.formBuilder.group({
      licensePlate: ['', Validators.required],
      validFrom: [null, Validators.required],
      validTo: [null, Validators.required],
    });
    this.getLicensePlates();
    this.showDialog = false;
  }

  async getLicensePlates(): Promise<void> {

    this.licensePlatesService.getApiLicensePlates().subscribe(
      (response: GetApiLicensePlatesResponse) => {
        console.log(response);
        // Map the response data to the LicensePlate interface
        this.licensePlatesTable = response.map((item) => {
          if (item.id === undefined || item.licensePlate === undefined || item.validFrom === undefined || item.validTo === undefined) {
            throw new Error('License plate data is incomplete.');
          }
          return {
            id: item.id,
            licensePlate: item.licensePlate,
            validFrom: new Date(item.validFrom),
            validTo: new Date(item.validTo)
          };
        });
        this.updateFilteredLicensePlates();
      },
      (error: any) => {
        console.error('Getting license plates failed:', error);
      }
    );

    this.updateFilteredLicensePlates();
  }

  addLicensePlate(): void {
    this.submitted = false;
    this.dialogLicensePlate = { id: '', licensePlate: '', validFrom: new Date(), validTo: new Date() };
    this.licensePlateForm.reset();
    this.licensePlateForm.patchValue(this.dialogLicensePlate);
    this.showDialog = true;
  }

  editLicensePlate(): void {
    this.dialogLicensePlate = { ...this.selectedLicensePlate };
    this.licensePlateForm.patchValue(this.dialogLicensePlate);
    this.showDialog = true;
  }

  async deleteLicensePlate(): Promise<void> {
    if (this.selectedLicensePlate) {
      this.confirmationService.confirm({
        message: 'Are you sure you want to delete the license plate ' + this.selectedLicensePlate.licensePlate.bold() + '?',
        header: 'Confirm',
        icon: 'pi pi-exclamation-triangle',
        accept: async () => {
          try {
            // Delete the selected license plate
            this.licensePlatesService.deleteApiLicensePlatesByLicensePlateId({ licensePlateId: this.selectedLicensePlate.id }).subscribe((response: MessageResponse) => {
              if (response.message) {
                // Remove the license plate from the licensePlatesTable
                this.licensePlatesTable = this.licensePlatesTable.filter(lp => lp.id !== this.selectedLicensePlate.id);
                this.updateFilteredLicensePlates();
                this.notifyMsg('success', 'Deleted', 'The license plate has been removed!');
              } else {
                this.notifyMsg('error', 'Error', 'Failed to delete license plate.');
              }
          })} catch (error) {
            this.notifyMsg('error', 'Error', 'Failed to delete license plate: ' + error);
          }
        }
      });
    } else {
      this.notifyMsg('error', 'Error', 'No license plate selected');
    }
  }

  async saveLicensePlate(): Promise<void> {
    this.submitted = true;
    // Checking if required fields are not empty and dates are valid before saving
    if (this.licensePlateForm.valid && this.isLicensePlateValid() && this.areDatesValid()) {
      const existingIndex = this.licensePlatesTable.findIndex(
        (lp) => lp.licensePlate === this.dialogLicensePlate.licensePlate
      );
      // Update this.dialogLicensePlate with form values
      this.dialogLicensePlate = { ...this.licensePlateForm.value };
      const formValue = this.licensePlateForm.value;
      const newLicensePlate: LicensePlateRequest = {
        ...formValue,
        validFrom: this.toLocalDateString(formValue.validFrom), // Convert to local date string
        validTo: this.toLocalDateString(formValue.validTo) // Convert to local date string
      };
      if (existingIndex !== -1) {
        try {
          // Modify an existing license plate
          this.licensePlatesService.putApiLicensePlatesByLicensePlateId({ licensePlateId: this.selectedLicensePlate.id, requestBody: newLicensePlate}).subscribe((response: PutApiLicensePlatesByLicensePlateIdResponse) => {
            if (response) {
              // Preserve the ID from the original license plate entry
              const updatedLicensePlate = { ...this.licensePlatesTable[existingIndex], ...this.dialogLicensePlate };
              // Update the license plate entry in licensePlatesTable
              this.licensePlatesTable[existingIndex] = updatedLicensePlate;
              this.updateFilteredLicensePlates();
              this.showDialog = false;
              this.notifyMsg('success', 'Edit license plate', 'Successfully edited!');
            } else {
              this.notifyMsg('error', 'Error', 'Failed to modify license plate.');
            }
        })} catch (error) {
            this.notifyMsg('error', 'Error', 'Failed to modify license plate: ' + error);
          }
      } else {

        try {
          this.licensePlatesService.postApiLicensePlates({ requestBody: newLicensePlate }).subscribe((response: LicensePlateCreateResponse) => {
            if (response && response.id) {
              // Check for complete data before adding the new license plate
              if (response.id === undefined) {
                throw new Error('License plate data id is incomplete.');
              }
              // Add the new license plate with the returned ID to the licensePlatesTable
              const newLicensePlateWithId: LicensePlate = {
                id: response.id,
                licensePlate: newLicensePlate.licensePlate,
                validFrom: new Date(newLicensePlate.validFrom),
                validTo: new Date(newLicensePlate.validTo)
              };
              this.licensePlatesTable.push({ ...newLicensePlateWithId });
              this.updateFilteredLicensePlates();
              this.notifyMsg('success', 'New license plate', 'Successfully added!');
              this.showDialog = false;
            } else {
              this.notifyMsg('error', 'Error', 'Failed to add license plate.');
            }
          }, error => {
            this.notifyMsg('error', 'Error', 'Failed to add license plate: ' + error.message);
          });
        } catch (error) {
          this.notifyMsg('error', 'Error', 'Failed to add license plate: ' + error);
        }
      }
    } else {
      this.notifyMsg('error', 'Error', 'Invalid license plate or dates.');
    }
  }

  async archiveExpiredLicensePlates(): Promise<void> {

    this.licensePlatesService.getApiLicensePlatesArchive().subscribe(
      (response: GetApiLicensePlatesResponse) => {
        // Map the response data to the LicensePlate interface
        let archiveData = response.map((item) => {
          if (item.id === undefined || item.licensePlate === undefined || item.validFrom === undefined || item.validTo === undefined) {
            throw new Error('License plate data is incomplete.');
          }
          return {
            id: item.id,
            licensePlate: item.licensePlate,
            validFrom: new Date(item.validFrom),
            validTo: new Date(item.validTo)
          };
        });
        console.log(response);
        this.updateFilteredLicensePlates();

      },
      (error: any) => {
        console.error('Getting archive license plates failed:', error);
      }
    );
    
  }

  isLicensePlateValid(): boolean {
    const licensePlate = this.licensePlateForm.get('licensePlate')?.value;
    return licensePlate && licensePlate.trim().length > 0;
  }

  areDatesValid(): boolean {
    const { validFrom, validTo } = this.licensePlateForm.value;
    return validFrom && validTo && validFrom <= validTo;
  }

  hideDialog(): void {
    this.submitted = false;
    this.showDialog = false;
  }

  notifyMsg(type: string, title: string, message: string): void {
    this.messageService.add({
      severity: type,
      summary: title,
      detail: message,
    });
  }

  filterGlobal(input: HTMLInputElement): void {
    this.globalFilter = input.value.trim();
    this.updateFilteredLicensePlates();
  }

  updateFilteredLicensePlates(): void {
    const filterValue = this.globalFilter.trim().toLowerCase();

    this.filteredLicensePlates = this.licensePlatesTable.filter(lp =>
      lp.licensePlate.toLowerCase().includes(filterValue) ||
      (this.datePipe.transform(lp.validFrom, 'yyyy-MM-dd')?.toLowerCase()?.includes(filterValue)) ||
      (this.datePipe.transform(lp.validTo, 'yyyy-MM-dd')?.toLowerCase()?.includes(filterValue))
    );
  }

  // Helper function to ensure date consistency
toLocalDateString = (dateString: string): string => {
  const date = new Date(dateString);
  // Adjust for time zone offset to keep the local date the same in UTC
  const adjustedDate = new Date(date.getTime() - (date.getTimezoneOffset() * 60000));
  return adjustedDate.toISOString().split('T')[0];
};

}
