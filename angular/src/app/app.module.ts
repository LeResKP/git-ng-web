import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule, Routes } from '@angular/router';

import { NgbModule } from '@ng-bootstrap/ng-bootstrap';


import { AppComponent } from './app.component';
import { DiffComponent } from './diff.component';
import { GitService } from './git.service';
import { LogListComponent } from './logs/log-list.component';
import { LogsModule } from './logs/logs.module';
import { MainComponent, RedirectBranchComponent } from './main.component';
import { SelectorComponent } from './selector.component';


const appRoutes: Routes = [
  { path: '', redirectTo: 'p/0', pathMatch: 'full'},
  {
    path: 'p/:id',
    component: MainComponent,
    children: [
      {
        path: '',
        component: RedirectBranchComponent,
      },
      {
        path: 'b/:branch/commits',
        component: LogListComponent,
      },
      {
        path: 'b/:branch/commits/:hash',
        component: LogListComponent,
      },
    ]
  },
];


@NgModule({
  declarations: [
    AppComponent,
    MainComponent,
    RedirectBranchComponent,
    SelectorComponent,
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    RouterModule.forRoot(appRoutes),
    NgbModule.forRoot(),
    LogsModule,
  ],
  providers: [GitService],
  bootstrap: [AppComponent]
})
export class AppModule { }
