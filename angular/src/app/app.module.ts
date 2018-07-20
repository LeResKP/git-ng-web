import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { RouterModule, Routes } from '@angular/router';

import { NgbModule } from '@ng-bootstrap/ng-bootstrap';


import { AppComponent } from './app.component';
import { GitService } from './git.service';
import { LogListComponent } from './logs/log-list.component';
import { LogsModule } from './logs/logs.module';
import { MainComponent, RedirectComponent } from './main.component';
import { SelectorComponent } from './selector.component';
import { CommitComponent } from './commit.component';
import { TreeComponent } from './tree.component';
import { BlobComponent } from './blob.component';
import { BreadcrumbComponent } from './breadcrumb';


const appRoutes: Routes = [
  {
    path: '',
    component: RedirectComponent,
  },
  {
    path: ':projectId/:sha',
    component: MainComponent,
    children: [
      {
        path: 'tree',
        children: [{
          path: '**',
          component: TreeComponent,
        }]
      },
      {
        path: 'blob',
        children: [{
          path: '**',
          component: BlobComponent,
        }]
      },
      {
        path: 'commits',
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
  }
];


@NgModule({
  declarations: [
    AppComponent,
    RedirectComponent,
    SelectorComponent,
    CommitComponent,
    TreeComponent,
    BlobComponent,
    BreadcrumbComponent,
    MainComponent,
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
