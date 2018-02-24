import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';

import { LogListComponent } from './log-list.component';
import { DiffComponent } from '../diff.component';


@NgModule({
  imports: [
    CommonModule,
    RouterModule,
  ],
  declarations: [
    DiffComponent,
    LogListComponent,
  ]
})
export class LogsModule { }
