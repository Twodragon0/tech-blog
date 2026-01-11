import {Composition} from 'remotion';
import {BlogVideo} from './BlogVideo';
import './index.css';

export const RemotionRoot: React.FC = () => {
	return (
		<>
			<Composition
				id="BlogVideo"
				component={BlogVideo}
				durationInFrames={300} // 10초 (30fps 기준, --frames 옵션으로 동적 조정)
				fps={30}
				width={1920}
				height={1080}
				defaultProps={{
					title: 'Blog Post Title',
					thumbnail: 'default-thumbnail.png',
					audioPath: 'audio.mp3',
				}}
			/>
		</>
	);
};
