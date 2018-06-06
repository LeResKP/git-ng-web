import { AfterViewChecked, Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import 'rxjs/add/operator/switchMap';

import { GitService } from './git.service';


@Component({
  selector: 'app-commit',
  templateUrl: `./diff.component.html`,
})
export class CommitComponent implements OnDestroy, OnInit, AfterViewChecked {

  public data$;
  private filename: string;

  constructor(private route: ActivatedRoute, private gitService: GitService, private router: Router) {}

  ngOnInit() {
    this.data$ = this.route.paramMap
        .switchMap((params: ParamMap) => {
          this.gitService.setCommitHash(params.get('hash'));
          document.querySelector('.autoscroll-right').scrollTop = 0;
          return this.gitService.getDiff(
            this.route.parent.parent.snapshot.params['id'], params.get('hash'));
        });

        this.route.fragment.subscribe((hash: string) => {
          this.filename = hash ? hash : null;
          // NOTE: will have no effect after the init, but will scroll when clicking on the link.
          this.scrollToAnchor();
        });
  }

  scrollToAnchor() {
    if (this.filename) {
      const elt: HTMLElement = document.getElementById(this.filename);
      if (elt) {
        elt.scrollIntoView();
        this.filename = null;
        return true;
      }
    }
    return false;
  }

  ngAfterViewChecked() {
    this.scrollToAnchor();
  }

  expand(line) {
    line.lines.map(l => l.type = 'context');
    line.type = 'hidden';
    return false;
  }

  ngOnDestroy() {
    this.gitService.setCommitHash(null);
  }

  close() {
    this.router.navigate([{outlets: {commit: null}} ], {relativeTo: this.route.parent});
  }

}
