import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule, Routes } from '@angular/router';

import { NgbModule } from '@ng-bootstrap/ng-bootstrap';


import { AppComponent } from './app.component';
import { GitService } from './git.service';
import { LogListComponent } from './logs/log-list.component';
import { LogsModule } from './logs/logs.module';
import { MainComponent, RedirectBranchComponent } from './main.component';
import { SelectorComponent } from './selector.component';
import { CommitComponent } from './commit.component';


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
        children: [
          {
            path: 'h/:hash',
            component: CommitComponent,
            outlet: 'commit',
          },
        ]
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
    CommitComponent,
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
