import { Component, OnInit } from '@angular/core';

import { GitService } from './git.service';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit {

  public projects;
  public project;

  constructor(private gitService: GitService) {}

  ngOnInit() {
    this.gitService.getProjects().subscribe(projects => {
      this.projects = projects;
      this.project = projects[0];
    });
  }


}
