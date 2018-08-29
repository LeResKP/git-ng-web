import { AfterViewChecked, Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap, Router } from '@angular/router';

import 'rxjs/add/operator/switchMap';

import { GitService } from './git.service';


const DEFAULT_DIFF_CONTEXT = 3;

@Component({
  selector: 'app-commit',
  templateUrl: `./diff.component.html`,
})
export class CommitComponent implements OnDestroy, OnInit, AfterViewChecked {

  public data;
  private projectId;
  private hash;
  private filename: string;

  public ignoreAllSpace = false;
  public context = DEFAULT_DIFF_CONTEXT;

  constructor(private route: ActivatedRoute, private gitService: GitService, private router: Router) {}

  ngOnInit() {
    this.projectId = this.route.parent.parent.snapshot.params['projectId'];
    this.route.paramMap
        .switchMap((params: ParamMap) => {
          this.ignoreAllSpace = params.get('ias') === 'true';
          this.context = +(params.get('unified') || DEFAULT_DIFF_CONTEXT);
          this.data = null;
          this.gitService.setCommitHash(params.get('hash'));
          document.querySelector('.autoscroll-right').scrollTop = 0;
          this.hash = params.get('hash');
          return this.gitService.getDiff(
            this.projectId, this.hash, this.ignoreAllSpace, this.context);
        }).subscribe(data => {
          this.data = data;
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

  expand(line, path, lines) {
    const index = lines.indexOf(line);
    this.gitService.getContextDiff(this.projectId, this.hash, path, line['context_data']
                                  ).subscribe(res => {
      lines.splice(index, 1, ...res as Array<any>);
    });
    return false;
  }

  ngOnDestroy() {
    this.gitService.setCommitHash(null);
  }

  close() {
    this.router.navigate([{outlets: {commit: null}} ], {relativeTo: this.route.parent});
  }

  ignoreAllSpaceChange(value) {
    this.ignoreAllSpace = value;
    this.router.navigate([{outlets: {commit: ['h', this.hash, {ias: this.ignoreAllSpace, unified: this.context}]}}], {relativeTo: this.route.parent});
  }

  unifiedChange(value) {
    this.context = value;
    this.router.navigate([{outlets: {commit: ['h', this.hash, {ias: this.ignoreAllSpace, unified: this.context}]}}], {relativeTo: this.route.parent});
  }

}
