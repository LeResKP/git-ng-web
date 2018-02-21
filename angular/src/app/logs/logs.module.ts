import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

import { LogListComponent } from './log-list.component';


@NgModule({
  imports: [
    CommonModule,
    RouterModule,
  ],
  declarations: [LogListComponent]
})
export class LogsModule { }
